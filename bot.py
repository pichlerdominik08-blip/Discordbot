import discord
from discord.ext import commands
from discord.ui import View, Button, Modal, TextInput, Select
import asyncio
import aiohttp
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN", "")
API_URL = os.getenv("API_URL", "http://localhost:8000")

intents = discord.Intents.default()
intents.guilds = True
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


# =====================================================
# API HELPER
# =====================================================

async def api_request(method: str, path: str, json_data=None):
    async with aiohttp.ClientSession() as session:
        url = f"{API_URL}{path}"
        async with session.request(method, url, json=json_data) as resp:
            if resp.status < 300:
                return await resp.json()
            return None


# =====================================================
# LOG SYSTEM
# =====================================================

async def send_log(guild: discord.Guild, action: str, user: discord.Member = None,
                   channel: discord.TextChannel = None, extra: str = None):
    config = await api_request("GET", f"/api/guilds/{guild.id}")
    if not config or not config.get("logs_enabled"):
        return

    log_channel_id = config.get("log_channel")
    if not log_channel_id:
        return

    log_channel = guild.get_channel(int(log_channel_id))
    if not log_channel:
        return

    embed = discord.Embed(
        title="Log System",
        color=discord.Color.dark_blue(),
        timestamp=discord.utils.utcnow()
    )
    embed.add_field(name="Aktion", value=action, inline=False)

    if user:
        embed.add_field(name="Ausgefuehrt von", value=f"{user.mention} ({user.id})", inline=False)
    if channel:
        embed.add_field(name="Betroffener Kanal",
                        value=f"Name: {channel.name}\nID: {channel.id}\n<#{channel.id}>",
                        inline=False)
    if extra:
        embed.add_field(name="Mehr Infos", value=extra, inline=False)

    await log_channel.send(embed=embed)


# =====================================================
# SAVE TRANSCRIPT (channel messages -> API)
# =====================================================

async def save_transcript(channel: discord.TextChannel, entry_id: int, guild_id: str):
    messages = []
    async for msg in channel.history(limit=500, oldest_first=True):
        messages.append({
            "entry_id": entry_id,
            "guild_id": guild_id,
            "channel_id": str(channel.id),
            "message_id": str(msg.id),
            "author_name": str(msg.author),
            "author_id": str(msg.author.id),
            "author_avatar": str(msg.author.display_avatar.url) if msg.author.display_avatar else None,
            "content": msg.content,
            "created_at": msg.created_at.isoformat()
        })

    if messages:
        await api_request("POST", "/api/messages/bulk", json_data=messages)


# =====================================================
# ON_MESSAGE: Save messages live to API
# =====================================================

@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        await bot.process_commands(message)
        return

    channel = message.channel
    if not isinstance(channel, discord.TextChannel):
        await bot.process_commands(message)
        return

    entry = await api_request("GET", f"/api/entries/by-channel/{channel.id}")
    if entry and entry.get("is_open"):
        await api_request("POST", "/api/messages", json_data={
            "entry_id": entry["id"],
            "guild_id": str(message.guild.id),
            "channel_id": str(channel.id),
            "message_id": str(message.id),
            "author_name": str(message.author),
            "author_id": str(message.author.id),
            "author_avatar": str(message.author.display_avatar.url) if message.author.display_avatar else None,
            "content": message.content,
            "created_at": message.created_at.isoformat()
        })

    await bot.process_commands(message)


# =====================================================
# CLOSE BUTTON (restart-safe)
# =====================================================

class CloseView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(
            Button(label="Schliessen", emoji="\U0001f512", style=discord.ButtonStyle.red, custom_id="close_global")
        )


@bot.event
async def on_interaction(interaction: discord.Interaction):
    if interaction.type != discord.InteractionType.component:
        return
    if interaction.data.get("custom_id") != "close_global":
        return

    channel = interaction.channel
    guild = interaction.guild
    category = channel.category

    await interaction.response.send_message("\U0001f512 Kanal wird geschlossen...", ephemeral=True)

    # Save transcript before deleting
    entry = await api_request("GET", f"/api/entries/by-channel/{channel.id}")
    if entry:
        await save_transcript(channel, entry["id"], str(guild.id))
        await api_request("PATCH", f"/api/entries/{entry['id']}/close")

    await send_log(guild, action="Kanal geschlossen", user=interaction.user, channel=channel)

    await asyncio.sleep(1)
    await channel.delete()

    if not category:
        return
    if not category.name.startswith("verstoesse-"):
        return

    await asyncio.sleep(0.5)
    category = guild.get_channel(category.id)

    if category and len(category.channels) == 0:
        await category.delete()
        return

    if category:
        channels = sorted(category.channels, key=lambda c: c.created_at)
        for index, ch in enumerate(channels, start=1):
            parts = ch.name.split("-")
            if len(parts) < 3:
                continue
            emoji = parts[0]
            rest = "-".join(parts[2:])
            new_name = f"{emoji}-{index}-{rest}"
            try:
                await ch.edit(name=new_name)
            except Exception:
                pass


# =====================================================
# PANEL
# =====================================================

class PanelView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Neuer Eintrag",
        style=discord.ButtonStyle.blurple,
        emoji="\U0001f4c2",
        custom_id="create_entry"
    )
    async def create(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_modal(MainModal())


# =====================================================
# MODAL
# =====================================================

class MainModal(Modal, title="Eintrag erstellen"):
    name_input = TextInput(
        label="Name",
        placeholder="z.B. Benutzername",
        max_length=30
    )
    description_input = TextInput(
        label="Beschreibung",
        placeholder="Beschreibe den Verstoss oder die Information",
        style=discord.TextStyle.paragraph,
        max_length=500
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            "Typ auswaehlen:",
            view=TypeView(self.name_input.value, self.description_input.value, interaction.user),
            ephemeral=True
        )


# =====================================================
# TYPE SELECT
# =====================================================

class TypeSelect(Select):
    def __init__(self, name, description, author):
        self.entry_name = name
        self.entry_description = description
        self.author = author

        super().__init__(
            placeholder="Typ auswaehlen...",
            options=[
                discord.SelectOption(label="Verstoss", value="v", emoji="\u26a0\ufe0f"),
                discord.SelectOption(label="Information", value="i", emoji="\U0001f4d8")
            ]
        )

    async def callback(self, interaction: discord.Interaction):
        config = await api_request("GET", f"/api/guilds/{interaction.guild.id}")
        if not config:
            await interaction.response.send_message("Kein Setup gefunden. Bitte zuerst !setup_order ausfuehren.", ephemeral=True)
            return

        # INFO
        if self.values[0] == "i":
            category = interaction.guild.get_channel(int(config["info_category"]))

            ch_name = f"info-{self.entry_name.lower().replace(' ', '-')}"
            channel = discord.utils.get(interaction.guild.text_channels, name=ch_name)

            embed = discord.Embed(title="\U0001f4d8 INFORMATION", color=discord.Color.blue())
            embed.add_field(name="Name", value=self.entry_name, inline=False)
            embed.add_field(name="Beschreibung", value=self.entry_description, inline=False)
            embed.set_author(name=str(self.author), icon_url=self.author.display_avatar.url)

            if not channel:
                role = interaction.guild.get_role(int(config["role_id"]))
                channel = await interaction.guild.create_text_channel(
                    name=ch_name,
                    category=category,
                    overwrites={
                        interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False),
                        role: discord.PermissionOverwrite(view_channel=True, send_messages=True)
                    }
                )

            await channel.send(embed=embed, view=CloseView())

            # Save to API
            await api_request("POST", "/api/entries", json_data={
                "guild_id": str(interaction.guild.id),
                "entry_type": "info",
                "name": self.entry_name,
                "description": self.entry_description,
                "author_name": str(self.author),
                "author_id": str(self.author.id),
                "author_avatar": str(self.author.display_avatar.url),
                "channel_id": str(channel.id),
                "channel_name": channel.name,
                "category_id": str(category.id) if category else None,
            })

            await send_log(interaction.guild, action="Info erstellt", user=self.author, channel=channel)
            await interaction.response.send_message(channel.mention, ephemeral=True)
            return

        # VIOLATION -> select severity
        await interaction.response.send_message(
            "Schwere waehlen:",
            view=SeverityView(self.entry_name, self.entry_description, self.author),
            ephemeral=True
        )


class TypeView(View):
    def __init__(self, n, d, a):
        super().__init__()
        self.add_item(TypeSelect(n, d, a))


# =====================================================
# SEVERITY SELECT (Violations)
# =====================================================

class SeveritySelect(Select):
    def __init__(self, name, description, author):
        self.entry_name = name
        self.entry_description = description
        self.author = author

        super().__init__(
            placeholder="Schwere auswaehlen...",
            options=[
                discord.SelectOption(label="Leicht", value="leicht", emoji="\U0001f7e2"),
                discord.SelectOption(label="Mittel", value="mittel", emoji="\U0001f7e1"),
                discord.SelectOption(label="Schwer", value="schwer", emoji="\U0001f534")
            ]
        )

    async def callback(self, interaction: discord.Interaction):
        config = await api_request("GET", f"/api/guilds/{interaction.guild.id}")
        if not config:
            await interaction.response.send_message("Kein Setup gefunden.", ephemeral=True)
            return

        role = interaction.guild.get_role(int(config["role_id"]))

        severity = self.values[0]
        emoji_map = {"leicht": "\U0001f7e2", "mittel": "\U0001f7e1", "schwer": "\U0001f534"}
        color_map = {
            "leicht": discord.Color.green(),
            "mittel": discord.Color.gold(),
            "schwer": discord.Color.red()
        }
        emoji = emoji_map[severity]
        color = color_map[severity]

        base = self.entry_name.lower().replace(" ", "-")
        category_name = f"verstoesse-{base}"

        category = discord.utils.get(interaction.guild.categories, name=category_name)
        if not category:
            category = await interaction.guild.create_category(
                category_name,
                overwrites={
                    interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False),
                    role: discord.PermissionOverwrite(view_channel=True, send_messages=True)
                }
            )

        number = len(category.channels) + 1
        channel = await interaction.guild.create_text_channel(
            name=f"{emoji}-{number}-verstoss-{base}",
            category=category
        )

        embed = discord.Embed(title=f"{emoji} VERSTOSS", color=color)
        embed.add_field(name="Name", value=self.entry_name, inline=False)
        embed.add_field(name="Schwere", value=severity, inline=False)
        embed.add_field(name="Beschreibung", value=self.entry_description, inline=False)
        embed.set_author(name=str(self.author), icon_url=self.author.display_avatar.url)

        await channel.send(embed=embed, view=CloseView())

        # Save to API
        await api_request("POST", "/api/entries", json_data={
            "guild_id": str(interaction.guild.id),
            "entry_type": "violation",
            "name": self.entry_name,
            "description": self.entry_description,
            "severity": severity,
            "author_name": str(self.author),
            "author_id": str(self.author.id),
            "author_avatar": str(self.author.display_avatar.url),
            "channel_id": str(channel.id),
            "channel_name": channel.name,
            "category_id": str(category.id),
        })

        await send_log(interaction.guild, f"VERSTOSS erstellt: {channel.name} von {self.author}")
        await interaction.response.send_message(channel.mention, ephemeral=True)


class SeverityView(View):
    def __init__(self, n, d, a):
        super().__init__()
        self.add_item(SeveritySelect(n, d, a))


# =====================================================
# SETUP
# =====================================================

SETUP_STATE = {}


@bot.command()
@commands.has_permissions(administrator=True)
async def setup_order(ctx):
    await ctx.send("Setup starten:", view=SetupStart())


class SetupStart(View):
    def __init__(self):
        super().__init__(timeout=300)

    @discord.ui.button(label="Start Setup", style=discord.ButtonStyle.green)
    async def start(self, interaction, button):
        SETUP_STATE[interaction.guild.id] = {}
        await interaction.response.send_message("Panel Channel waehlen:", view=StepPanel(), ephemeral=True)


class StepPanel(View):
    def __init__(self):
        super().__init__(timeout=300)

    @discord.ui.select(cls=discord.ui.ChannelSelect)
    async def panel(self, interaction, select):
        SETUP_STATE[interaction.guild.id]["panel"] = select.values[0]
        await interaction.response.send_message("Info Kategorie waehlen:", view=StepInfo(), ephemeral=True)


class StepInfo(View):
    def __init__(self):
        super().__init__(timeout=300)

    @discord.ui.select(cls=discord.ui.ChannelSelect, channel_types=[discord.ChannelType.category])
    async def info(self, interaction, select):
        SETUP_STATE[interaction.guild.id]["info"] = select.values[0]
        await interaction.response.send_message("Rolle waehlen:", view=StepRole(), ephemeral=True)


class StepRole(View):
    def __init__(self):
        super().__init__(timeout=300)

    @discord.ui.select(cls=discord.ui.RoleSelect)
    async def role(self, interaction, select):
        SETUP_STATE[interaction.guild.id]["role"] = select.values[0]
        await interaction.response.send_message("Logs aktivieren?", view=StepLogs(), ephemeral=True)


class StepLogs(View):
    def __init__(self):
        super().__init__(timeout=300)

    @discord.ui.button(label="Mit Logs", style=discord.ButtonStyle.green)
    async def yes(self, interaction, button):
        await interaction.response.send_message("Log Channel waehlen:", view=StepLogChannel(True), ephemeral=True)

    @discord.ui.button(label="Ohne Logs", style=discord.ButtonStyle.red)
    async def no(self, interaction, button):
        await finish_setup(interaction, False, None)


class StepLogChannel(View):
    def __init__(self, enabled):
        super().__init__(timeout=300)
        self.enabled = enabled

    @discord.ui.select(cls=discord.ui.ChannelSelect, channel_types=[discord.ChannelType.text])
    async def log(self, interaction: discord.Interaction, select):
        await interaction.response.defer(ephemeral=True)
        await finish_setup(interaction, True, select.values[0])


# =====================================================
# FINISH SETUP
# =====================================================

async def finish_setup(interaction, logs, log_channel):
    data = SETUP_STATE.get(interaction.guild.id)
    guild = interaction.guild

    await api_request("POST", "/api/guilds", json_data={
        "guild_id": str(guild.id),
        "guild_name": guild.name,
        "panel_channel": str(data["panel"].id),
        "info_category": str(data["info"].id),
        "role_id": str(data["role"].id),
        "logs_enabled": logs,
        "log_channel": str(log_channel.id) if log_channel else None,
    })

    SETUP_STATE.pop(interaction.guild.id, None)
    await interaction.followup.send("Setup abgeschlossen!", ephemeral=True)
    await send_panel(guild)


# =====================================================
# SEND PANEL
# =====================================================

async def send_panel(guild):
    config = await api_request("GET", f"/api/guilds/{guild.id}")
    if not config:
        return

    channel = guild.get_channel(int(config["panel_channel"]))
    role = guild.get_role(int(config["role_id"]))

    if channel:
        await channel.set_permissions(guild.default_role, view_channel=False)
        await channel.set_permissions(role, view_channel=True)

        msg = await channel.send(
            "## \U0001f4c2 **Bestellbereich**\nKlicke auf den Button, um einen neuen Eintrag zu erstellen.",
            view=PanelView()
        )

        await api_request("POST", "/api/guilds", json_data={
            "guild_id": str(guild.id),
            "guild_name": guild.name,
            "panel_channel": str(channel.id),
            "panel_message": str(msg.id),
            "info_category": config.get("info_category"),
            "role_id": config.get("role_id"),
            "logs_enabled": bool(config.get("logs_enabled")),
            "log_channel": config.get("log_channel"),
        })


# =====================================================
# REPAIR COMMAND
# =====================================================

@bot.tree.command(name="repair", description="Repariert das Panel, falls es nach dem Neustart fehlt.")
@commands.has_permissions(administrator=True)
async def repair(interaction: discord.Interaction):
    guild = interaction.guild
    config = await api_request("GET", f"/api/guilds/{guild.id}")

    if not config:
        return await interaction.response.send_message("Keine Config gefunden. Bitte Setup ausfuehren.", ephemeral=True)

    panel_channel = guild.get_channel(int(config.get("panel_channel", 0)))
    role = guild.get_role(int(config.get("role_id", 0)))

    if not panel_channel:
        return await interaction.response.send_message("Panel Channel existiert nicht mehr. Bitte Setup neu machen.", ephemeral=True)

    if role:
        await panel_channel.set_permissions(guild.default_role, view_channel=False)
        await panel_channel.set_permissions(role, view_channel=True)

    # Remove old panels
    async for msg in panel_channel.history(limit=50):
        if msg.author == bot.user and "Bestellbereich" in msg.content:
            await msg.delete()

    # Send new panel
    await panel_channel.send(
        "## \U0001f4c2 **Bestellbereich**\nKlicke auf den Button, um einen neuen Eintrag zu erstellen.",
        view=PanelView()
    )

    await interaction.response.send_message("Reparatur abgeschlossen: Panel wurde gefixt.", ephemeral=True)


# =====================================================
# ON READY
# =====================================================

@bot.event
async def on_ready():
    await bot.wait_until_ready()
    await asyncio.sleep(2)

    print(f"Online als {bot.user}")

    bot.add_view(PanelView())
    bot.add_view(CloseView())

    # Check all guilds for existing panels
    guilds_resp = await api_request("GET", "/api/guilds")
    if not guilds_resp:
        guilds_resp = []

    for config in guilds_resp:
        guild = bot.get_guild(int(config["guild_id"]))
        if not guild:
            continue

        panel_channel = guild.get_channel(int(config.get("panel_channel", 0)))
        role = guild.get_role(int(config.get("role_id", 0)))

        if not panel_channel:
            continue

        if role:
            await panel_channel.set_permissions(guild.default_role, view_channel=False)
            await panel_channel.set_permissions(role, view_channel=True)

        already_exists = False
        async for msg in panel_channel.history(limit=50):
            if msg.author == bot.user and "Bestellbereich" in msg.content:
                already_exists = True
                break

        if not already_exists:
            await panel_channel.send(
                "## \U0001f4c2 **Bestellbereich**\nKlicke auf den Button, um einen neuen Eintrag zu erstellen.",
                view=PanelView()
            )
            print(f"Panel erstellt in {guild.name}")
        else:
            print(f"Panel gefunden in {guild.name}")

    await bot.tree.sync()
    print("Slash-Befehle synchronisiert")
    print("Bot bereit!")


bot.run(TOKEN)
