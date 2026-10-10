import discord
from discord.ext import commands
import yt_dlp
import asyncio
from flask import Flask
import threading
import os

app = Flask(__name__)
@app.route('/')
def home(): return "Bot de Musica Online!"
def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
threading.Thread(target=run_flask).start()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Musica listo: {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"Sincronizados: {len(synced)}")
    except Exception as e:
        print(e)

@bot.tree.command(name="play", description="Reproduce una cancion")
async def play(interaction: discord.Interaction, cancion: str):
    await interaction.response.defer()
    if not interaction.user.voice:
        await interaction.followup.send("❌ Métete a un canal de voz primero!")
        return
    channel = interaction.user.voice.channel
    vc = interaction.guild.voice_client
    if not vc:
        vc = await channel.connect()
    elif vc.channel!= channel:
        await vc.move_to(channel)
    try:
        import imageio_ffmpeg as ffmpeg_bin
        ydl_opts = {'format': 'bestaudio', 'noplaylist': True, 'quiet': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch:{cancion}", download=False)['entries'][0]
            url = info['url']
            title = info.get('title', 'Cancion')
        source = discord.FFmpegPCMAudio(url, executable=ffmpeg_bin.get_ffmpeg_exe(), before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5", options="-vn")
        if vc.is_playing():
            vc.stop()
        vc.play(source)
        await interaction.followup.send(f"🎵 Reproduciendo: **{title}**")
    except Exception as e:
        await interaction.followup.send(f"❌ Error: {e}")

@bot.tree.command(name="stop", description="Para la musica")
async def stop(interaction: discord.Interaction):
    if interaction.guild.voice_client:
        await interaction.guild.voice_client.disconnect()
        await interaction.response.send_message("⏹️ Musica parada")
    else:
        await interaction.response.send_message("No estoy en voz")

bot.run(os.getenv("DISCORD_TOKEN"))
