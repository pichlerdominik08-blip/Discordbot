import aiosqlite
import os

DB_PATH = os.getenv("DB_PATH", "/data/app.db")

async def get_db():
    db = await aiosqlite.connect(DB_PATH)
    db.row_factory = aiosqlite.Row
    return db

async def init_db():
    db = await get_db()
    await db.executescript("""
        CREATE TABLE IF NOT EXISTS guilds (
            guild_id TEXT PRIMARY KEY,
            guild_name TEXT,
            panel_channel TEXT,
            panel_message TEXT,
            info_category TEXT,
            role_id TEXT,
            logs_enabled INTEGER DEFAULT 0,
            log_channel TEXT
        );

        CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            guild_id TEXT NOT NULL,
            entry_type TEXT NOT NULL,  -- 'violation' or 'info'
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            severity TEXT,  -- 'leicht', 'mittel', 'schwer' (only for violations)
            author_name TEXT,
            author_id TEXT,
            author_avatar TEXT,
            channel_id TEXT,
            channel_name TEXT,
            category_id TEXT,
            is_open INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            closed_at TIMESTAMP,
            FOREIGN KEY (guild_id) REFERENCES guilds(guild_id)
        );

        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entry_id INTEGER NOT NULL,
            guild_id TEXT NOT NULL,
            channel_id TEXT NOT NULL,
            message_id TEXT NOT NULL UNIQUE,
            author_name TEXT,
            author_id TEXT,
            author_avatar TEXT,
            content TEXT,
            created_at TIMESTAMP,
            FOREIGN KEY (entry_id) REFERENCES entries(id)
        );
    """)
    await db.commit()
    await db.close()
