import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import os

# ================= CONFIGURAÇÃO =================
TOKEN = os.getenv("TOKEN")
bot = telebot.TeleBot(TOKEN)

GRUPO_ID = -1003629208122  # ID do grupo VIP
ADMIN_ID = 8431121309       # Seu ID

# ================= DEFINIÇÃO DE CORES E GRUPOS =================
vermelhos = {1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36}
pretos = {2,4,6,8,10,11,13,15,17,20,22,24,26,28,29,31,33,35}
altos = set(range(19,37))
baixos = set(range(1,19))

# Estratégias renomeadas
grupo_A = {3,6,9,13,16,19,23,26,29,33,36}  # DG du GRAL
grupo_B = {19,15,32,0,26,3,35,12,28,8,23,10,5}  # Makako777

# ================= VARIÁVEIS GLOBAIS =================
numeros = []
placar = {"par":0,"impar":0,"preto":0,"vermelho":0,"alto":0,"baixo":0}
painel_id = None
mensagens_reset = []

entrada_ativa = None
grupo_entrada = None
gales = 0
numero_alerta = None
nome_jogada = ""

filtro_ativo = False
numeros_filtro = []
gales_filtro = 0

banca = 0
aguardando_banca = False

# ================= FUNÇÕES =================
def resetar():
    """Reseta contadores e variáveis de rodadas"""
    global numeros, placar, entrada_ativa, gales, numero_alerta
    global filtro_ativo, numeros_filtro, gales_filtro, grupo_entrada, nome_jogada

    numeros.clear()
    placar.update({"par":0,"impar":0,"preto":0,"vermelho":0,"alto":0,"baixo":0})
    entrada_ativa = None
    gales = 0
    numero_alerta = None
    grupo_entrada = None
    nome_jogada = ""
    filtro_ativo = False
    numeros_filtro.clear()
    gales_filtro = 0

def limpar_mensagens():
    """Apaga mensagens antigas do painel"""
    global mensagens_reset
    for msg_id in mensagens_reset:
        try:
            bot.delete_message(GRUPO_ID, msg_id)
        except:
            continue
    mensagens_reset.clear()

# ================= TECLADO 0–36 =================
def teclado():
    """Gera teclado interativo 0–36"""
    kb = InlineKeyboardMarkup(row_width=6)
    botoes = []
    for i in range(37):
        cor = ""
        if i in pretos:
            cor = "⚫"
        elif i in vermelhos:
            cor = "🔴"
        botoes.append(InlineKeyboardButton(f"{i}{cor}", callback_data=str(i)))
    kb.add(*botoes)
    return kb

# ================= PAINEL =================
def painel_texto():
    """Texto do painel atualizado"""
    return f"""
🎯 SNIPER VIP ({len(numeros)}/15 rodadas)

⚫ Preto: {placar['preto']} | 🔴 Vermelho: {placar['vermelho']}
🔵 Par: {placar['par']} | 🟣 Ímpar: {placar['impar']}
⬆ Alto: {placar['alto']} | ⬇ Baixo: {placar['baixo']}
"""

# ================= ATUALIZA PLACAR =================
def atualizar_placar(num):
    if num != 0:
        if num % 2 == 0:
            placar["par"] += 1
        else:
            placar["impar"] += 1

        if num in pretos:
            placar["preto"] += 1
        if num in vermelhos:
            placar["vermelho"] += 1

        if num in altos:
            placar["alto"] += 1
        if num in baixos:
            placar["baixo"] += 1

# ================= GESTOR DE BANCA =================
def enviar_gestor(numeros_aposta):
    """Envia sugestões de apostas com base na banca"""
    global mensagens_reset
    if banca <= 0:
        return

    conservador = round(banca * 0.02,2)
    medio = round(banca * 0.05,2)
    agressivo = round(banca * 0.10,2)

    msg = bot.send_message(GRUPO_ID,
f"""💰 GESTÃO DE BANCA - {nome_jogada}

Entrada: {sorted(numeros_aposta)}

🔹 Conservador: R${conservador} por ficha
🔸 Médio: R${medio} por ficha
🔺 Agressivo: R${agressivo} por ficha
""")
    mensagens_reset.append(msg.message_id)

# ================= ESTRATEGIAS =================
def verificar_sinal_10_rodadas():
    """Checa se Estratégia A ou B deve disparar"""
    global entrada_ativa, grupo_entrada, gales, numero_alerta, nome_jogada
    …
