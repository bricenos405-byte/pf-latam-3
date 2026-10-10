import discord
from discord.ext import commands
import wavelink
import asyncio
import os

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)

TOKEN = os.getenv("DISCORD_TOKEN") or "TU_TOKEN_AQUI"

@bot.event
async def on_ready():
    print(f"BOT LISTO ✅ {bot.user}")
    nodes = [
        wavelink.Node(uri="http://lavalink.jirayu.net:2333", password="youshallnotpass"),
        wavelink.Node(uri="https://lava-v4.oops.wtf:443", password="oops.wtf"),
        wavelink.Node(uri="http://5.178.111.207:2000", password="youshallnotpass"),
    ]
    await wavelink.Pool.connect(nodes=nodes, client=bot, cache_capacity=100)
    print("NODOS INTENTANDO CONECTAR...")
    try:
        synced = await bot.tree.sync()
        print(f"Comandos sincronizados: {len(synced)}")
    except Exception as e:
        print(e)

@bot.event
async def on_wavelink_node_ready(payload: wavelink.NodeReadyEventPayload):
    print(f"NODO CONECTADO ✅ {payload.node.uri}")

@bot.event
async def on_wavelink_track_end(payload: wavelink.TrackEndEventPayload):
    if payload.player:
        if not payload.player.queue.is_empty:
            await payload.player.play(payload.player.queue.get())

@bot.hybrid_command(name="play", description="Reproduce una canción")
async def play(ctx: commands.Context, *, query: str):
    if not ctx.guild:
        return

    if not ctx.author.voice:
        await ctx.send("¡Métete a un canal de voz primero, mi ñaño! 🎤", ephemeral=True)
        return

    if not ctx.voice_client:
        await ctx.author.voice.channel.connect(cls=wavelink.Player)
    else:
        if ctx.voice_client.channel!= ctx.author.voice.channel:
            await ctx.voice_client.move_to(ctx.author.voice.channel)

    player: wavelink.Player = ctx.voice_client

    await ctx.defer()

    tracks = await wavelink.Playable.search(query)

    if not tracks:
        await ctx.send(f"No encontré nada para: {query} 😢")
        return

    track = tracks[0]

    if player.playing:
        player.queue.put(track)
        await ctx.send(f"Agregada a la cola: **{track.title}**")
    else:
        await player.play(track)
        await ctx.send(f"Reproduciendo ahora: **{track.title}** 🎶")

@bot.hybrid_command(name="stop", description="Detiene la música y se sale")
async def stop(ctx: commands.Context):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("Me fui, mi rey! 👋")
    else:
        await ctx.send("No estoy en voz")

@bot.hybrid_command(name="skip", description="Salta la canción")
async def skip(ctx: commands.Context):
    if ctx.voice_client and ctx.voice_client.playing:
        await ctx.voice_client.stop()
        await ctx.send("⏭️ Siguiente!")

@bot.hybrid_command(name="pause", description="Pausa la música")
async def pause(ctx: commands.Context):
    if ctx.voice_client:
        await ctx.voice_client.pause(True)
        await ctx.send("⏸️ Pausado")

@bot.hybrid_command(name="resume", description="Reanuda la música")
async def resume(ctx: commands.Context):
    if ctx.voice_client:
        await ctx.voice_client.pause(False)
        await ctx.send("▶️ Reanudando!")

bot.run(TOKEN)
