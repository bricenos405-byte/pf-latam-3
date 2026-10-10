import discord
from discord.ext import commands
import wavelink
import os
from flask import Flask
import threading

app = Flask(__name__)
@app.route('/')
def home(): return "PF LATAM 03 Bot Online - Multi Node"
def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
threading.Thread(target=run_flask).start()

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.guilds = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Listo: {bot.user}")
    await bot.tree.sync()

    # 3 SERVIDORES - Si uno falla, usa el otro
    nodes = [
        wavelink.Node(uri="https://lavalink.jirayu.net:443", password="youshallnotpass", secure=True),
        wavelink.Node(uri="https://lava-v4.ajieblogs.eu.org:443", password="https://dsc.gg/ajidevserver", secure=True),
        wavelink.Node(uri="http://5.230.37.169:2333", password="youshallnotpass", secure=False)
    ]
    try:
        await wavelink.Pool.connect(client=bot, nodes=nodes)
        print("Intentando conectar nodos Lavalink...")
    except Exception as e:
        print(f"Error Pool: {e}")

@bot.event
async def on_wavelink_node_ready(payload: wavelink.NodeReadyEventPayload):
    print(f"✅ Nodo conectado: {payload.node.uri}")

@bot.tree.command(name="play", description="Reproduce una cancion")
async def play(interaction: discord.Interaction, cancion: str):
    if not interaction.user.voice or not interaction.user.voice.channel:
        await interaction.response.send_message("❌ Métete a voz primero!", ephemeral=True)
        return

    # Verificar que haya nodo conectado
    if not wavelink.Pool.nodes or not any(n.status == wavelink.NodeStatus.CONNECTED for n in wavelink.Pool.nodes.values()):
        await interaction.response.send_message("⏳ Conectando servidor de música... espera 10 seg y prueba de nuevo. Los servidores gratuitos tardan.", ephemeral=True)
        # Reintentar conectar
        try:
            nodes = [
                wavelink.Node(uri="https://lavalink.jirayu.net:443", password="youshallnotpass", secure=True),
                wavelink.Node(uri="http://5.230.37.169:2333", password="youshallnotpass", secure=False)
            ]
            await wavelink.Pool.connect(client=bot, nodes=nodes)
        except:
            pass
        return

    await interaction.response.defer()
    channel = interaction.user.voice.channel

    player: wavelink.Player = interaction.guild.voice_client
    if not player:
        try:
            player = await channel.connect(cls=wavelink.Player, self_deaf=True)
        except Exception as e:
            await interaction.followup.send(f"❌ No pude entrar a voz (permisos): {e}")
            return

    try:
        tracks = await wavelink.Pool.fetch_tracks(f'ytsearch:{cancion}')
        if not tracks:
            await interaction.followup.send(f"❌ No encontré {cancion}")
            return

        track = tracks[0]
        await player.play(track)
        await interaction.followup.send(f"🎵 Reproduciendo: **{track.title}**")
    except Exception as e:
        await interaction.followup.send(f"❌ Error reproduciendo: {e}")

@bot.tree.command(name="stop", description="Para la musica")
async def stop(interaction: discord.Interaction):
    player = interaction.guild.voice_client
    if player:
        await player.disconnect()
        await interaction.response.send_message("⏹️ Desconectado")
    else:
        await interaction.response.send_message("No estoy en voz")

bot.run(os.getenv("DISCORD_TOKEN"))
