from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.database import get_db, init_db
from pydantic import BaseModel
from typing import Optional
import os


@asynccontextmanager
async def lifespan(app: FastAPI):
    os.makedirs(os.path.dirname(os.getenv("DB_PATH", "/data/app.db")), exist_ok=True)
    await init_db()
    yield


app = FastAPI(lifespan=lifespan)

# Disable CORS. Do not remove this for full-stack development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


@app.get("/healthz")
async def healthz():
    return {"status": "ok"}


# =====================================================
# GUILD ENDPOINTS
# =====================================================

class GuildCreate(BaseModel):
    guild_id: str
    guild_name: str
    panel_channel: Optional[str] = None
    panel_message: Optional[str] = None
    info_category: Optional[str] = None
    role_id: Optional[str] = None
    logs_enabled: bool = False
    log_channel: Optional[str] = None


@app.post("/api/guilds")
async def upsert_guild(guild: GuildCreate):
    db = await get_db()
    await db.execute("""
        INSERT INTO guilds (guild_id, guild_name, panel_channel, panel_message, info_category, role_id, logs_enabled, log_channel)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(guild_id) DO UPDATE SET
            guild_name=excluded.guild_name,
            panel_channel=excluded.panel_channel,
            panel_message=excluded.panel_message,
            info_category=excluded.info_category,
            role_id=excluded.role_id,
            logs_enabled=excluded.logs_enabled,
            log_channel=excluded.log_channel
    """, (guild.guild_id, guild.guild_name, guild.panel_channel, guild.panel_message,
          guild.info_category, guild.role_id, int(guild.logs_enabled), guild.log_channel))
    await db.commit()
    await db.close()
    return {"status": "ok"}


@app.get("/api/guilds")
async def list_guilds():
    db = await get_db()
    cursor = await db.execute("SELECT * FROM guilds")
    rows = await cursor.fetchall()
    await db.close()
    return [dict(row) for row in rows]


@app.get("/api/guilds/{guild_id}")
async def get_guild(guild_id: str):
    db = await get_db()
    cursor = await db.execute("SELECT * FROM guilds WHERE guild_id = ?", (guild_id,))
    row = await cursor.fetchone()
    await db.close()
    if not row:
        raise HTTPException(status_code=404, detail="Guild not found")
    return dict(row)


# =====================================================
# ENTRY ENDPOINTS (Verstöße + Infos)
# =====================================================

class EntryCreate(BaseModel):
    guild_id: str
    entry_type: str
    name: str
    description: str
    severity: Optional[str] = None
    author_name: Optional[str] = None
    author_id: Optional[str] = None
    author_avatar: Optional[str] = None
    channel_id: Optional[str] = None
    channel_name: Optional[str] = None
    category_id: Optional[str] = None


@app.post("/api/entries")
async def create_entry(entry: EntryCreate):
    db = await get_db()
    cursor = await db.execute("""
        INSERT INTO entries (guild_id, entry_type, name, description, severity,
                           author_name, author_id, author_avatar, channel_id, channel_name, category_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (entry.guild_id, entry.entry_type, entry.name, entry.description, entry.severity,
          entry.author_name, entry.author_id, entry.author_avatar, entry.channel_id,
          entry.channel_name, entry.category_id))
    entry_id = cursor.lastrowid
    await db.commit()
    await db.close()
    return {"id": entry_id, "status": "created"}


@app.get("/api/entries")
async def list_entries(
    guild_id: Optional[str] = None,
    entry_type: Optional[str] = None,
    is_open: Optional[int] = None
):
    db = await get_db()
    query = "SELECT * FROM entries WHERE 1=1"
    params: list[str | int] = []
    if guild_id:
        query += " AND guild_id = ?"
        params.append(guild_id)
    if entry_type:
        query += " AND entry_type = ?"
        params.append(entry_type)
    if is_open is not None:
        query += " AND is_open = ?"
        params.append(is_open)
    query += " ORDER BY created_at DESC"
    cursor = await db.execute(query, params)
    rows = await cursor.fetchall()
    await db.close()
    return [dict(row) for row in rows]


@app.get("/api/entries/{entry_id}")
async def get_entry(entry_id: int):
    db = await get_db()
    cursor = await db.execute("SELECT * FROM entries WHERE id = ?", (entry_id,))
    row = await cursor.fetchone()
    await db.close()
    if not row:
        raise HTTPException(status_code=404, detail="Entry not found")
    return dict(row)


@app.patch("/api/entries/{entry_id}/close")
async def close_entry(entry_id: int):
    db = await get_db()
    await db.execute(
        "UPDATE entries SET is_open = 0, closed_at = CURRENT_TIMESTAMP WHERE id = ?",
        (entry_id,)
    )
    await db.commit()
    await db.close()
    return {"status": "closed"}


# =====================================================
# MESSAGE / TRANSCRIPT ENDPOINTS
# =====================================================

class MessageCreate(BaseModel):
    entry_id: int
    guild_id: str
    channel_id: str
    message_id: str
    author_name: Optional[str] = None
    author_id: Optional[str] = None
    author_avatar: Optional[str] = None
    content: Optional[str] = None
    created_at: Optional[str] = None


@app.post("/api/messages")
async def save_message(msg: MessageCreate):
    db = await get_db()
    await db.execute("""
        INSERT OR IGNORE INTO messages (entry_id, guild_id, channel_id, message_id,
                                        author_name, author_id, author_avatar, content, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (msg.entry_id, msg.guild_id, msg.channel_id, msg.message_id,
          msg.author_name, msg.author_id, msg.author_avatar, msg.content, msg.created_at))
    await db.commit()
    await db.close()
    return {"status": "saved"}


@app.post("/api/messages/bulk")
async def save_messages_bulk(messages: list[MessageCreate]):
    db = await get_db()
    for msg in messages:
        await db.execute("""
            INSERT OR IGNORE INTO messages (entry_id, guild_id, channel_id, message_id,
                                            author_name, author_id, author_avatar, content, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (msg.entry_id, msg.guild_id, msg.channel_id, msg.message_id,
              msg.author_name, msg.author_id, msg.author_avatar, msg.content, msg.created_at))
    await db.commit()
    await db.close()
    return {"status": "saved", "count": len(messages)}


@app.get("/api/entries/{entry_id}/messages")
async def get_transcript(entry_id: int):
    db = await get_db()
    cursor = await db.execute(
        "SELECT * FROM messages WHERE entry_id = ? ORDER BY created_at ASC",
        (entry_id,)
    )
    rows = await cursor.fetchall()
    await db.close()
    return [dict(row) for row in rows]


# =====================================================
# STATS
# =====================================================

@app.get("/api/guilds/{guild_id}/stats")
async def get_guild_stats(guild_id: str):
    db = await get_db()

    cursor = await db.execute(
        "SELECT COUNT(*) as count FROM entries WHERE guild_id = ? AND entry_type = 'violation'",
        (guild_id,)
    )
    violations = (await cursor.fetchone())["count"]

    cursor = await db.execute(
        "SELECT COUNT(*) as count FROM entries WHERE guild_id = ? AND entry_type = 'info'",
        (guild_id,)
    )
    infos = (await cursor.fetchone())["count"]

    cursor = await db.execute(
        "SELECT COUNT(*) as count FROM entries WHERE guild_id = ? AND is_open = 1",
        (guild_id,)
    )
    open_entries = (await cursor.fetchone())["count"]

    cursor = await db.execute(
        "SELECT COUNT(*) as count FROM messages WHERE guild_id = ?",
        (guild_id,)
    )
    total_messages = (await cursor.fetchone())["count"]

    await db.close()
    return {
        "violations": violations,
        "infos": infos,
        "open": open_entries,
        "total_messages": total_messages
    }


# =====================================================
# LOOKUP BY CHANNEL
# =====================================================

@app.get("/api/entries/by-channel/{channel_id}")
async def get_entry_by_channel(channel_id: str):
    db = await get_db()
    cursor = await db.execute("SELECT * FROM entries WHERE channel_id = ?", (channel_id,))
    row = await cursor.fetchone()
    await db.close()
    if not row:
        raise HTTPException(status_code=404, detail="Entry not found for this channel")
    return dict(row)
