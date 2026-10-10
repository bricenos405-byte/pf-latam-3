import discord
from discord.ext import commands
from discord import app_commands
import datetime
import json
import os

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Archivo para guardar los pontos
ARQUIVO_PONTOS = "pontos.json"

def carregar_pontos():
    if os.path.exists(ARQUIVO_PONTOS):
        with open(ARQUIVO_PONTOS, 'r') as f:
            return json.load(f)
    return {}

def salvar_pontos(dados):
    with open(ARQUIVO_PONTOS, 'w') as f:
        json.dump(dados, f, indent=4)

pontos = carregar_pontos()

class PontoView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Abrir", style=discord.ButtonStyle.green, custom_id="abrir")
    async def abrir(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Usa /ponto para registrar tu punto", ephemeral=True)

    @discord.ui.button(label="Terminar", style=discord.ButtonStyle.red, custom_id="terminar")
    async def terminar(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_id = str(interaction.user.id)
        if user_id in pontos and pontos[user_id]["ativo"]:
            inicio = datetime.datetime.fromisoformat(pontos[user_id]["inicio"])
            agora = datetime.datetime.now()
            tempo_total = agora - inicio
            
            # Descontar pausas
            if "tempo_pausa" in pontos[user_id]:
                tempo_total -= datetime.timedelta(seconds=pontos[user_id]["tempo_pausa"])

            horas = int(tempo_total.total_seconds() // 3600)
            minutos = int((tempo_total.total_seconds() % 3600) // 60)

            pontos[user_id]["ativo"] = False
            pontos[user_id]["fim"] = agora.isoformat()
            salvar_pontos(pontos)

            embed = discord.Embed(
                title="📁 Bate-ponto PF LATAM 3",
                description=f"**Usuário:** {interaction.user.mention}\n**Início:** {inicio.strftime('%d/%m/%Y %H:%M')}\n**Fim:** {agora.strftime('%d/%m/%Y %H:%M')}\n\n**⏱️ Tempo total:** {horas}h {minutos}min",
                color=0x00ff00
            )
            embed.set_footer(text="Sistema desenvolvido pela Nyox Store • PF LATAM 3")
            await interaction.response.edit_message(embed=embed, view=None)
            await interaction.followup.send(f"✅ {interaction.user.mention} Ponto finalizado! Trabalhou {horas}h {minutos}min em PF LATAM 3 🥃", ephemeral=False)
        else:
            await interaction.response.send_message("❌ Você não tem ponto aberto!", ephemeral=True)

@bot.event
async def on_ready():
    print(f"✅ Bot conectado como {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"Sincronizados {len(synced)} comandos")
    except Exception as e:
        print(e)

@bot.tree.command(name="ponto", description="Registra seu ponto na PF LATAM 3")
async def ponto(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    agora = datetime.datetime.now()
    
    if user_id in pontos and pontos[user_id].get("ativo", False):
        # Já está em ponto, mostra status
        inicio = datetime.datetime.fromisoformat(pontos[user_id]["inicio"])
        tempo = agora - inicio
        horas = int(tempo.total_seconds() // 3600)
        minutos = int((tempo.total_seconds() % 3600) // 60)
        
        embed = discord.Embed(
            title="📂 Bate-ponto PF LATAM 3",
            description=f"**Usuário:** {interaction.user.mention}\n**Início:** {inicio.strftime('%d de %B de %Y %H:%M')}\n**Tempo atual:** {horas}h {minutos}min\n**Status:** 🟢 Em serviço",
            color=0x0099ff
        )
        embed.set_footer(text="Sistema desenvolvido pela Nyox Store • Versão gratuita")
        await interaction.response.send_message(embed=embed, view=PontoView())
    else:
        # Inicia ponto
        pontos[user_id] = {
            "inicio": agora.isoformat(),
            "ativo": True,
            "tempo_pausa": 0
        }
        salvar_pontos(pontos)
        
        embed = discord.Embed(
            title="📂 Bate-ponto PF LATAM 3",
            description=f"**Usuário:** {interaction.user.mention}\n**Início:** {agora.strftime('%d de %B de %Y %H:%M')}\n**Pausa:** --\n**Tempo:** 0h 0min\n**Status:** 🟢 Ponto iniciado",
            color=0x0099ff
        )
        embed.set_footer(text="Sistema desenvolvido pela Nyox Store • Versão gratuita")
        await interaction.response.send_message(embed=embed, view=PontoView())
        await interaction.followup.send(f"✅ {interaction.user.mention} Ponto registrado en PF LATAM 3 🥃")

# IMPORTANTE: Pon tu token en Render en Environment Variables
import os
bot.run(os.getenv("DISCORD_TOKEN"))
