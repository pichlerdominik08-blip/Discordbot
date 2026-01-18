import os
import discord
from discord import app_commands

GUILD_ID = 1324456758076506112

intents = discord.Intents.default()
intents.members = True
intents.guilds = True

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

SECURITY_LOG_CHANNEL_ID = 1355308249758306465  # ID vom Info-/Log-Kanal


@client.event
async def on_ready():
    guild = discord.Object(id=GUILD_ID)
    await tree.sync(guild=guild)
    print("READY – Commands synced")


@tree.command(name="say",
              description="Der Bot sendet eine Nachricht in einen Kanal",
              guild=discord.Object(id=GUILD_ID))
@app_commands.default_permissions(administrator=True)
@app_commands.describe(text="Was soll der Bot sagen?",
                       channel="In welchen Kanal soll die Nachricht?")
async def say(interaction: discord.Interaction, text: str,
              channel: discord.TextChannel):
    await channel.send(text)
    await interaction.response.send_message(f"✅ Gesendet in {channel.mention}",
                                            ephemeral=True)


@tree.command(name="sus",
              description="Jemand ist sus",
              guild=discord.Object(id=GUILD_ID))
@app_commands.describe(user="Wer ist sus?")
async def sus(interaction: discord.Interaction, user: discord.Member):
    await interaction.response.send_message(
        f"📮 **{user.mention} ist extrem sus…** 👀")


import random


@tree.command(name="iq",
              description="Zeigt den IQ eines Users",
              guild=discord.Object(id=GUILD_ID))
@app_commands.describe(user="Wessen IQ?")
async def iq(interaction: discord.Interaction, user: discord.Member):
    iq_value = random.randint(50, 160)
    await interaction.response.send_message(
        f"🧠 Der IQ von **{user.display_name}** ist **{iq_value}**")


@tree.command(name="boom",
              description="Boom!",
              guild=discord.Object(id=GUILD_ID))
async def boom(interaction: discord.Interaction):
    await interaction.response.send_message("💣 BOOOOM 💥")


@tree.command(name="sleep",
              description="Jemand schläft ein",
              guild=discord.Object(id=GUILD_ID))
@app_commands.describe(user="Wer schläft?")
async def sleep(interaction: discord.Interaction, user: discord.Member):
    await interaction.response.send_message(
        f"😴 **{user.display_name}** ist eingeschlafen… schnarch 💤")


import random

INSULTS = [
    "ist der lebende Beweis, dass Sauerstoff verschwendet wird.",
    "hat so wenig Hirnaktivität, dass selbst Windows XP schneller denkt.",
    "würde bei einem Intelligenztest durchfallen – ohne Fragen.",
    "ist der Grund, warum Anleitungen Warnhinweise haben.",
    "hat mehr Lags im Kopf als WLAN bei McDonald's.",
    "existiert nur, um andere besser aussehen zu lassen.",
    "ist wie ein Bug – keiner weiß warum er da ist.",
    "hat den IQ einer leeren Batterie.",
    "wurde offensichtlich im Tutorial übersprungen.",
    "wenn Dummheit weh tun würde, wäre er/sie im Dauerkrankenstand."
]


@tree.command(name="insult",
              description="Beleidigt jemanden maximal",
              guild=discord.Object(id=GUILD_ID))
@app_commands.describe(user="Wer soll komplett geroastet werden?")
async def insult(interaction: discord.Interaction, user: discord.Member):
    roast = random.choice(INSULTS)
    await interaction.response.send_message(f"🔥 **{user.mention}** {roast}")


@tree.command(name="lock",
              description="Sperrt einen Textkanal",
              guild=discord.Object(id=GUILD_ID))
@app_commands.default_permissions(administrator=True)
@app_commands.describe(channel="Welcher Textkanal?")
async def lock(interaction: discord.Interaction, channel: discord.TextChannel):
    overwrite = channel.overwrites_for(interaction.guild.default_role)
    overwrite.send_messages = False
    await channel.set_permissions(interaction.guild.default_role,
                                  overwrite=overwrite)

    await interaction.response.send_message(
        f"🔒 **#{channel.name}** wurde gesperrt")


@tree.command(name="unlock",
              description="Entsperrt einen Textkanal",
              guild=discord.Object(id=GUILD_ID))
@app_commands.default_permissions(administrator=True)
@app_commands.describe(channel="Welcher Textkanal?")
async def unlock(interaction: discord.Interaction,
                 channel: discord.TextChannel):
    overwrite = channel.overwrites_for(interaction.guild.default_role)
    overwrite.send_messages = True
    await channel.set_permissions(interaction.guild.default_role,
                                  overwrite=overwrite)

    await interaction.response.send_message(
        f"🔓 **#{channel.name}** wurde entsperrt")


@tree.command(name="vlock",
              description="Sperrt einen Sprachkanal",
              guild=discord.Object(id=GUILD_ID))
@app_commands.default_permissions(administrator=True)
@app_commands.describe(channel="Welcher Sprachkanal?")
async def vlock(interaction: discord.Interaction,
                channel: discord.VoiceChannel):
    overwrite = channel.overwrites_for(interaction.guild.default_role)
    overwrite.connect = False
    await channel.set_permissions(interaction.guild.default_role,
                                  overwrite=overwrite)

    await interaction.response.send_message(
        f"🔒 **{channel.name}** wurde gesperrt")


@tree.command(name="vunlock",
              description="Entsperrt einen Sprachkanal",
              guild=discord.Object(id=GUILD_ID))
@app_commands.default_permissions(administrator=True)
@app_commands.describe(channel="Welcher Sprachkanal?")
async def vunlock(interaction: discord.Interaction,
                  channel: discord.VoiceChannel):
    overwrite = channel.overwrites_for(interaction.guild.default_role)
    overwrite.connect = True
    await channel.set_permissions(interaction.guild.default_role,
                                  overwrite=overwrite)

    await interaction.response.send_message(
        f"🔓 **{channel.name}** wurde entsperrt")


@tree.command(name="giverole",
              description="Gibt einem User eine Rolle",
              guild=discord.Object(id=GUILD_ID))
@app_commands.default_permissions(administrator=True)
@app_commands.describe(member="Welcher User?", role="Welche Rolle?")
async def giverole(interaction: discord.Interaction, member: discord.Member,
                   role: discord.Role):
    if role in member.roles:
        await interaction.response.send_message(
            "❌ User hat diese Rolle bereits", ephemeral=True)
        return

    await member.add_roles(role)

    await interaction.response.send_message(
        f"✅ {role.mention} wurde **{member.mention}** gegeben")


@tree.command(name="removerole",
              description="Entfernt eine Rolle von einem User",
              guild=discord.Object(id=GUILD_ID))
@app_commands.default_permissions(administrator=True)
@app_commands.describe(member="Welcher User?", role="Welche Rolle?")
async def removerole(interaction: discord.Interaction, member: discord.Member,
                     role: discord.Role):
    if role not in member.roles:
        await interaction.response.send_message("❌ User hat diese Rolle nicht",
                                                ephemeral=True)
        return

    await member.remove_roles(role)

    await interaction.response.send_message(
        f"🗑️ {role.mention} wurde **{member.mention}** entfernt")


@tree.command(name="giverole_all",
              description="Gibt eine Rolle an ALLE (everyone)",
              guild=discord.Object(id=GUILD_ID))
@app_commands.default_permissions(administrator=True)
@app_commands.describe(role="Welche Rolle soll jeder bekommen?")
async def giverole_all(interaction: discord.Interaction, role: discord.Role):
    await interaction.response.defer(thinking=True)

    count = 0
    for member in interaction.guild.members:
        if role not in member.roles:
            try:
                await member.add_roles(role)
                count += 1
            except:
                pass

    await interaction.followup.send(
        f"✅ **{role.name}** wurde an **{count} Mitglieder** vergeben")


@tree.command(name="removerole_all",
              description="Entfernt eine Rolle von ALLEN",
              guild=discord.Object(id=GUILD_ID))
@app_commands.default_permissions(administrator=True)
@app_commands.describe(role="Welche Rolle entfernen?")
async def removerole_all(interaction: discord.Interaction, role: discord.Role):
    await interaction.response.defer(thinking=True)

    count = 0
    for member in interaction.guild.members:
        if role in member.roles:
            try:
                await member.remove_roles(role)
                count += 1
            except:
                pass

    await interaction.followup.send(
        f"🗑️ **{role.name}** wurde von **{count} Mitglieder** entfernt")




import asyncio

@tree.command(
    name="sicherheitsmassnahme_on",
    description="Aktiviert den Sicherheitsmodus (alle Kanäle sperren)",
    guild=discord.Object(id=GUILD_ID)
)
@app_commands.default_permissions(administrator=True)
@app_commands.describe(
    duration="Dauer in Minuten (z.B. 10, 30, 60)",
    reason="Grund für die Sicherheitsmaßnahme"
)
async def sicherheit_on(
    interaction: discord.Interaction,
    duration: int,
    reason: str
):
    await interaction.response.defer(thinking=True)

    guild = interaction.guild
    everyone = guild.default_role

    # 🔒 Textkanäle sperren
    for channel in guild.text_channels:
        overwrite = channel.overwrites_for(everyone)
        overwrite.send_messages = False
        await channel.set_permissions(everyone, overwrite=overwrite)

    # 🔒 Sprachkanäle sperren
    for channel in guild.voice_channels:
        overwrite = channel.overwrites_for(everyone)
        overwrite.connect = False
        await channel.set_permissions(everyone, overwrite=overwrite)

    # 📢 Log-Nachricht
    log_channel = guild.get_channel(SECURITY_LOG_CHANNEL_ID)
    if log_channel:
        await log_channel.send(
            "🚨 **SICHERHEITSMASSNAHME AKTIVIERT** 🚨\n"
            f"👮 Aktiviert von: {interaction.user.mention}\n"
            f"⏱ Dauer: **{duration} Minuten**\n"
            f"📌 Grund: **{reason}**\n\n"
            "🔒 Alle Text- & Sprachkanäle wurden gesperrt."
        )

    await interaction.followup.send(
        "🔒 Sicherheitsmaßnahme wurde **aktiviert**",
        ephemeral=True
    )

    # ⏱️ Timer
    await asyncio.sleep(duration * 60)

    # 🔓 Automatisch entsperren
    for channel in guild.text_channels:
        overwrite = channel.overwrites_for(everyone)
        overwrite.send_messages = True
        await channel.set_permissions(everyone, overwrite=overwrite)

    for channel in guild.voice_channels:
        overwrite = channel.overwrites_for(everyone)
        overwrite.connect = True
        await channel.set_permissions(everyone, overwrite=overwrite)

    if log_channel:
        await log_channel.send(
            "🟢 **SICHERHEITSMASSNAHME AUTOMATISCH AUFGEHOBEN**"
        )



@tree.command(
    name="sicherheitsmassnahme_off",
    description="Hebt die Sicherheitsmaßnahme sofort auf",
    guild=discord.Object(id=GUILD_ID)
)
@app_commands.default_permissions(administrator=True)
async def sicherheit_off(interaction: discord.Interaction):
    await interaction.response.defer(thinking=True)

    guild = interaction.guild
    everyone = guild.default_role

    for channel in guild.text_channels:
        overwrite = channel.overwrites_for(everyone)
        overwrite.send_messages = True
        await channel.set_permissions(everyone, overwrite=overwrite)

    for channel in guild.voice_channels:
        overwrite = channel.overwrites_for(everyone)
        overwrite.connect = True
        await channel.set_permissions(everyone, overwrite=overwrite)

    log_channel = guild.get_channel(SECURITY_LOG_CHANNEL_ID)
    if log_channel:
        await log_channel.send(
            "🟢 **SICHERHEITSMASSNAHME MANUELL AUFGEHOBEN**"
        )

    await interaction.followup.send(
        "🟢 Sicherheitsmaßnahme wurde **sofort deaktiviert**"
    )










client.run("TOKEN")
