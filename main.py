import discord
from discord.ext import commands
import random, os
from flask import Flask
from threading import Thread

app = Flask('')
@app.route('/')
def home():
    return "PF LATAM 3 - ONLINE 24/7"
def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive():
    t = Thread(target=run)
    t.start()

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)

chistes = [
"Un maracucho: ¡Vergación dame una fría! ¿Polar o Zulia? ¡No, fría de temperatura!",
"¿En qué se parece un borracho colombiano a un venezolano? Dicen 'la última y me voy' y se van a las 6am",
"El miche entra como amigo, habla como abogado y sale como dueño de la casa",
"Venezolano en Medellín: Parce, ¿qué es chamo? Como parce pero más pana, vale",
"Un paisa tomando: Este guaro está suave, es que es miche venezolano, pega retroactivo"
]

@bot.event
async def on_ready():
    print(f"PF LATAM 3 conectado como {bot.user}")
    await bot.tree.sync()

@bot.tree.command(name="chiste", description="Chiste colombiano y venezolano")
async def chiste(interaction: discord.Interaction):
    await interaction.response.send_message(random.choice(chistes))

@bot.tree.command(name="ponto", description="Registra tu ponto")
async def ponto(interaction: discord.Interaction):
    await interaction.response.send_message(f"✅ {interaction.user.mention} Ponto registrado en PF LATAM 3 🥃")

@bot.tree.command(name="play", description="Reproduce música")
async def play(interaction: discord.Interaction, cancion: str):
    await interaction.response.send_message(f"🎵 Buscando: **{cancion}**")

@bot.tree.command(name="ticket-setup", description="Configura tickets")
async def ticket_setup(interaction: discord.Interaction):
    await interaction.response.send_message("🎫 Sistema de tickets PF LATAM 3 configurado")

keep_alive()
bot.run(os.getenv("TOKEN"))
