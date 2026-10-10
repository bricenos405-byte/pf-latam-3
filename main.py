import os
import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime
import yt_dlp
from flask import Flask
from threading import Thread

# Servidor web para Render
app = Flask('')
@app.route('/')
def home():
    return "Bot Online!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    Thread(target=run).start()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

pontos = {}

class PontoView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Iniciar Expediente", style=discord.ButtonStyle.green)
    async def iniciar(self, interaction: discord.Interaction, button: discord.ui.Button):
        pontos[interaction.user.id] = {"inicio": datetime.now()}
        await interaction.response.send_message(f"✅ {interaction.user.mention} Expediente iniciado!", ephemeral=True)

    @discord.ui.button(label="Finalizar", style=discord.ButtonStyle.red)
    async def finalizar(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id in pontos:
            inicio = pontos[interaction.user.id]["inicio"]
            tiempo = datetime.now() - inicio
            horas = tiempo.total_seconds() / 3600
            await interaction.response.send_message(f"✅ Trabajaste {horas:.2f} horas", ephemeral=True)
            del pontos[interaction.user.id]

@bot.tree.command(name="ponto", description="Bate tu ponto")
async def ponto(interaction: discord.Interaction):
    embed = discord.Embed(title="⏰ Sistema de Ponto", description="Controla tu expediente", color=0x00ff00)
    await interaction.response.send_message(embed=embed, view=PontoView())

@bot.tree.command(name="play", description="Reproduce música")
async def play(interaction: discord.Interaction, cancion: str):
    await interaction.response.defer()
    if not interaction.user.voice:
        await interaction.followup.send("❌ Debes estar en un canal de voz!")
        return
    channel = interaction.user.voice.channel
    if not interaction.guild.voice_client:
        await channel.connect()
    voice_client = interaction.guild.voice_client
    ydl_opts = {'format': 'bestaudio', 'noplaylist': True, 'quiet': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch:{cancion}", download=False)['entries'][0]
        url = info['url']
        title = info['title']
    source = discord.FFmpegPCMAudio(url, before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5", options="-vn")
    voice_client.play(source)
    await interaction.followup.send(f"🎵 Reproduciendo: **{title}**")

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Bot {bot.user} online")

keep_alive()
bot.run(os.getenv('DISCORD_TOKEN'))
