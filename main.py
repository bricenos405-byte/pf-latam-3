import discord
from discord.ext import commands
import wavelink
import os

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.guilds = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ BOT LISTO: {bot.user}")
    await bot.tree.sync()
    print("✅ Comandos sincronizados")

    nodes = [
        wavelink.Node(uri="https://lavalink.jirayu.net:443", password="youshallnotpass", identifier="MAIN", secure=True),
        wavelink.Node(uri="https://lava-v4.ajieblogs.eu.org:443", password="https://dsc.gg/ajidevserver", identifier="BACKUP", secure=True),
    ]

    try:
        await wavelink.Pool.connect(client=bot, nodes=nodes)
        print("🔄 Conectando a Lavalink...")
    except Exception as e:
        print(f"❌ Error Pool: {e}")

@bot.event
async def on_wavelink_node_ready(payload: wavelink.NodeReadyEventPayload):
    print(f"🔥 NODO CONECTADO: {payload.node.identifier} - LISTO PARA MUSICA")

@bot.tree.command(name="play", description="Reproduce una cancion")
async def play(interaction: discord.Interaction, cancion: str):
    if not interaction.user.voice or not interaction.user.voice.channel:
        await interaction.response.send_message("❌ Métete a voz primero!", ephemeral=True)
        return

    if not wavelink.Pool.nodes:
        await interaction.response.send_message("⏳ Aún conectando el servidor de música... dame 20 seg y prueba de nuevo. Revisa los logs en Render que diga 'NODO CONECTADO'", ephemeral=True)
        return

    await interaction.response.defer()
    channel = interaction.user.voice.channel

    player = interaction.guild.voice_client
    if not player:
        player = await channel.connect(cls=wavelink.Player, self_deaf=True)

    tracks = await wavelink.Pool.fetch_tracks(f'ytsearch:{cancion}')
    if not tracks:
        await interaction.followup.send("❌ No encontré la canción")
        return

    track = tracks[0]
    await player.play(track)
    await interaction.followup.send(f"🎵 Reproduciendo: **{track.title}** - Ayer sonó esta misma, mi ñaño!")

@bot.tree.command(name="stop", description="Para la musica")
async def stop(interaction: discord.Interaction):
    player = interaction.guild.voice_client
    if player:
        await player.disconnect()
        await interaction.response.send_message("⏹️ Desconectado")
    else:
        await interaction.response.send_message("No estoy en voz")

bot.run(os.getenv("DISCORD_TOKEN"))
