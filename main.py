import discord
from discord.ext import commands
import yt_dlp
import asyncio
from flask import Flask
import threading
import os

app = Flask(__name__)
@app.route('/')
def home(): return "Bot Online!"
def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
threading.Thread(target=run_flask).start()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Listo: {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"Sincronizados {len(synced)} comandos")
    except Exception as e:
        print(e)

def get_audio(query, use_sc=False):
    import imageio_ffmpeg as ffmpeg_bin
    ffmpeg_exe = ffmpeg_bin.get_ffmpeg_exe()
    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'quiet': True,
        'default_search': 'scsearch' if use_sc else 'ytsearch',
        'source_address': '0.0.0.0',
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'ios', 'web'],
                'po_token': ['web+bgutil', 'ios+bgutil']
            }
        }
    }
    prefix = "scsearch1:" if use_sc else "ytsearch1:"
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"{prefix}{query}", download=False)
        entry = info['entries'][0] if 'entries' in info else info
        return entry, ffmpeg_exe

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
        loop = asyncio.get_event_loop()
        try:
            print("Intentando YouTube...")
            info, ffmpeg_exe = await loop.run_in_executor(None, lambda: get_audio(cancion, False))
        except Exception as e:
            print(f"YouTube bloqueado, cambiando a SoundCloud: {e}")
            await interaction.followup.send("⚠️ YouTube bloqueó Render, probando en SoundCloud...")
            info, ffmpeg_exe = await loop.run_in_executor(None, lambda: get_audio(cancion, True))

        url = info['url']
        title = info.get('title', cancion)
        source = discord.FFmpegPCMAudio(url, executable=ffmpeg_exe, before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5", options="-vn")
        if vc.is_playing():
            vc.stop()
        vc.play(source)
        await interaction.followup.send(f"🎵 Reproduciendo: **{title}**")
    except Exception as e:
        print(f"ERROR FINAL: {e}")
        await interaction.followup.send(f"❌ Error: {e}")

@bot.tree.command(name="stop", description="Para la musica")
async def stop(interaction: discord.Interaction):
    if interaction.guild.voice_client:
        await interaction.guild.voice_client.disconnect()
        await interaction.response.send_message("⏹️ Parado")
    else:
        await interaction.response.send_message("No estoy en voz")

bot.run(os.getenv("DISCORD_TOKEN"))
