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
intents.voice_states = True
intents.guilds = True
bot = commands.Bot(command_prefix="!", intents=intents)

LAVA_HOST = "lava-v4.ajieblogs.eu.org"
LAVA_PORT = 443
LAVA_PASS = "https://dsc.gg/ajidevserver"

@bot.event
async def on_ready():
    print(f"Listo: {bot.user}")
    await bot.tree.sync()
    try:
        node = wavelink.Node(uri=f"https://{LAVA_HOST}:{LAVA_PORT}", password=LAVA_PASS, secure=True)
        await wavelink.Pool.connect(client=bot, nodes=[node])
        print("Lavalink OK")
    except Exception as e:
        print(f"Lavalink Error: {e}")

@bot.event
async def on_wavelink_node_ready(payload: wavelink.NodeReadyEventPayload):
    print(f"Nodo listo: {payload.node.identifier}")

@bot.tree.command(name="play", description="Reproduce una cancion")
async def play(interaction: discord.Interaction, cancion: str):
    if not interaction.user.voice or not interaction.user.voice.channel:
        await interaction.response.send_message("❌ Métete a un canal de voz primero, ñaño!", ephemeral=True)
        return

    await interaction.response.defer()
    channel = interaction.user.voice.channel

    # Buscar player existente o crear
    player: wavelink.Player = interaction.guild.voice_client
    if not player:
        try:
            player = await channel.connect(cls=wavelink.Player, self_deaf=True)
        except Exception as e:
            print(f"Error conectando voz: {e}")
            await interaction.followup.send(f"❌ No pude entrar a voz. Revisa que tenga permiso de conectar: {e}")
            return

    tracks = await wavelink.Pool.fetch_tracks(f'ytsearch:{cancion}')
    if not tracks:
        await interaction.followup.send(f"❌ No encontré {cancion}")
        return

    track = tracks[0]
    await player.play(track)
    await interaction.followup.send(f"🎵 Reproduciendo: **{track.title}** - {track.author}")

@bot.tree.command(name="stop", description="Para la musica")
async def stop(interaction: discord.Interaction):
    player = interaction.guild.voice_client
    if player:
        await player.disconnect()
        await interaction.response.send_message("⏹️ Desconectado")
    else:
        await interaction.response.send_message("No estoy en voz")

bot.run(os.getenv("DISCORD_TOKEN"))
