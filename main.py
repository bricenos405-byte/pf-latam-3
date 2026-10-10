import discord
from discord.ext import commands
import wavelink
import os
from flask import Flask
import threading

app = Flask(__name__)
@app.route('/')
def home(): return "PF LATAM 03 Bot Online!"
def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
threading.Thread(target=run_flask).start()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Servidor Lavalink gratis (no se cae)
LAVA_HOST = "lava-v4.ajieblogs.eu.org"
LAVA_PORT = 443
LAVA_PASS = "https://dsc.gg/ajidevserver"
LAVA_SECURE = True

@bot.event
async def on_ready():
    print(f"Listo: {bot.user}")
    await bot.tree.sync()
    print("Comandos sincronizados")
    # Conectar a Lavalink
    try:
        node = wavelink.Node(uri=f'{"https" if LAVA_SECURE else "http"}://{LAVA_HOST}:{LAVA_PORT}', password=LAVA_PASS, secure=LAVA_SECURE)
        await wavelink.Pool.connect(client=bot, nodes=[node])
        print(f"Lavalink conectado: {LAVA_HOST}")
    except Exception as e:
        print(f"Error Lavalink: {e}")

@bot.event
async def on_wavelink_node_ready(payload: wavelink.NodeReadyEventPayload):
    print(f"Nodo Lavalink listo: {payload.node.identifier}")

@bot.tree.command(name="play", description="Reproduce una cancion")
async def play(interaction: discord.Interaction, cancion: str):
    if not interaction.user.voice:
        await interaction.response.send_message("❌ Métete a un canal de voz primero!", ephemeral=True)
        return

    await interaction.response.defer()
    channel = interaction.user.voice.channel

    try:
        player = await channel.connect(cls=wavelink.Player, self_deaf=True)
    except:
        player = interaction.guild.voice_client

    if not player:
        await interaction.followup.send("❌ No pude conectarme a voz")
        return

    # Buscar en YouTube via Lavalink (el bypass definitivo)
    tracks = await wavelink.Pool.fetch_tracks(f'ytsearch:{cancion}')

    if not tracks:
        await interaction.followup.send(f"❌ No encontré: {cancion}")
        return

    track = tracks[0]
    await player.play(track)

    await interaction.followup.send(f"🎵 Reproduciendo: **{track.title}** - {track.author}")

@bot.tree.command(name="stop", description="Para la musica y desconecta")
async def stop(interaction: discord.Interaction):
    player = interaction.guild.voice_client
    if player:
        await player.disconnect()
        await interaction.response.send_message("⏹️ Música parada y desconectado")
    else:
        await interaction.response.send_message("No estoy en voz")

@bot.tree.command(name="skip", description="Salta la cancion")
async def skip(interaction: discord.Interaction):
    player: wavelink.Player = interaction.guild.voice_client
    if player and player.playing:
        await player.stop()
        await interaction.response.send_message("⏭️ Siguiente!")
    else:
        await interaction.response.send_message("No hay nada sonando")

bot.run(os.getenv("DISCORD_TOKEN"))
