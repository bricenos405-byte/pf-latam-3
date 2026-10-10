import discord
from discord.ext import commands
import datetime
import json
import os
from flask import Flask
from threading import Thread

app = Flask('')
@app.route('/')
def home():
    return "PF LATAM 3 - ONLINE 24/7"
def run():
    app.run(host='0.0.0.0',port=8080)
def keep_alive():
    t = Thread(target=run)
    t.start()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

pontos = {}

class PontoView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    @discord.ui.button(label="Pausar", style=discord.ButtonStyle.blurple)
    async def pausar(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("⏸️ Pausado", ephemeral=True)
    @discord.ui.button(label="Terminar", style=discord.ButtonStyle.red)
    async def terminar(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_id = str(interaction.user.id)
        if user_id in pontos:
            inicio = datetime.datetime.fromisoformat(pontos[user_id]["inicio"])
            agora = datetime.datetime.now()
            total = agora - inicio
            h = int(total.total_seconds() // 3600)
            m = int((total.total_seconds() % 3600) // 60)
            del pontos[user_id]
            embed = discord.Embed(title="📁 Bate-ponto Finalizado", description=f"**Usuario:** {interaction.user.mention}\n**Inicio:** {inicio.strftime('%d/%m %H:%M')}\n**Fin:** {agora.strftime('%d/%m %H:%M')}\n\n**Tiempo Total: {h}h {m}min**", color=0x00ff00)
            await interaction.response.edit_message(embed=embed, view=None)

@bot.event
async def on_ready():
    print(f"Bot {bot.user} online")
    await bot.tree.sync()

@bot.tree.command(name="ponto", description="Bate tu ponto")
async def ponto(interaction: discord.Interaction):
    agora = datetime.datetime.now()
    user_id = str(interaction.user.id)
    pontos[user_id] = {"inicio": agora.isoformat()}
    embed = discord.Embed(title="📂 Bate-ponto PF LATAM 3", description=f"**Usuario:** {interaction.user.mention}\n**Inicio:** {agora.strftime('%d de %B de %Y %H:%M')}\n**Pausa:** --\n**Tiempo:** 0h 0min\n**Status:** 🟢 En servicio", color=0x0099ff)
    embed.set_footer(text="PF LATAM 3 • Nyox Store")
    await interaction.response.send_message(embed=embed, view=PontoView())

keep_alive()
bot.run(os.getenv("DISCORD_TOKEN"))
