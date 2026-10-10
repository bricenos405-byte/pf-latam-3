import discord
from discord.ext import commands
import wavelink
import os
from flask import Flask
import threading

app = Flask(__name__)
@app.route('/')
def home():
    return "PF LATAM 03 - BOT ONLINE"

def run_flask():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

threading.Thread(target=run_flask, daemon=True).start()

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
    wavelink.Node(uri="http://lavalink.jirayu.net:2333", password="youshallnotpass", secure=False),
    wavelink.Node(uri="https://lava-v4.oops.wtf:443", password="oops.wtf"),
    wavelink.Node(uri="http://5.178.111.207:2000", password="youshallnotpass", secure=False),
    ]
    await wavelink.Pool.connect(client=bot, nodes=nodes)
    print("🔄 Conectando Lavalink...")

@bot.event
async def on_wavelink_node_ready(payload: wavelink.NodeReadyEventPayload):
    print(f"🔥 NODO CONECTADO: {payload.node.uri} - LISTO PARA MUSICA")

@bot.tree.command(name="play", description="Reproduce una cancion")
async def play(interaction: discord.Interaction, cancion: str):
    if not interaction.user.voice or not interaction.user.voice.channel:
        await interaction.response.send_message("❌ Métete a voz primero!", ephemeral=True)
        return
    if not wavelink.Pool.nodes or not wavelink.Pool.nodes[0].is_connected:
        await interaction.response.send_message("⏳ Conectando música... espera 20s y prueba de nuevo", ephemeral=True)
        return
    await interaction.response.defer()
    channel = interaction.user.voice.channel
    player = interaction.guild.voice_client
    if not player:
        player = await channel.connect(cls=wavelink.Player, self_deaf=True)
    tracks = await wavelink.Pool.fetch_tracks(f'ytsearch:{cancion}')
    if not tracks:
        await interaction.followup.send("❌ No encontré")
        return
    await player.play(tracks[0])
    await interaction.followup.send(f"🎵 Reproduciendo: **{tracks[0].title}**")

@bot.tree.command(name="stop", description="Para")
async def stop(interaction: discord.Interaction):
    player = interaction.guild.voice_client
    if player:
        await player.disconnect()
    await interaction.response.send_message("⏹️ Listo")

bot.run(os.getenv("DISCORD_TOKEN"))
