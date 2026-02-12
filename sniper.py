import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import os

TOKEN = os.getenv("TOKEN")
bot = telebot.TeleBot(TOKEN)

ADMINS = [8431121309]
GRUPO_ID = -1003629208122

MAX_RODADAS = 15
numeros = []
alerta_enviado = False
mensagem_grupo_id = None
saldos = {}

grupo_A = {3,6,9,13,16,19,23,26,29,33,36}
grupo_B = {19,15,32,0,26,3,35,12,28,8,25,10,5}

vermelhos = {1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36}

# ================= CLASSIFICAR =================

def classificar(numero):
    if numero == 0:
        return None, None, None

    cor = "vermelho" if numero in vermelhos else "preto"
    par = "par" if numero % 2 == 0 else "impar"
    altura = "baixo" if numero <= 18 else "alto"

    return cor, par, altura

# ================= TABELA ADM =================

def criar_tabela():
    markup = InlineKeyboardMarkup(row_width=6)
    botoes = []
    for i in range(37):
        botoes.append(InlineKeyboardButton(str(i), callback_data=str(i)))
    markup.add(*botoes)
    return markup

# ================= GESTOR =================

def enviar_gestor(qtd_numeros):
    texto = f"""
💰 GESTÃO DE BANCA

Entrada Normal:
Aposte $1 por número
Total números: {qtd_numeros}

1/2 banca
Banca total

Gerencie conforme seu saldo.
"""
    bot.send_message(GRUPO_ID, texto)

# ================= INICIAR TELA AO VIVO =================

def iniciar_painel_grupo():
    global mensagem_grupo_id

    texto = """
🔥 SNIPER AO VIVO 🔥

Rodadas: 0/15
Faltam: 15

Aguardando números...
"""
    msg = bot.send_message(GRUPO_ID, texto)
    mensagem_grupo_id = msg.message_id

# ================= ATUALIZAR TELA =================

def atualizar_grupo():
    rodada = len(numeros)
    faltam = MAX_RODADAS - rodada

    texto = f"""
🔥 SNIPER AO VIVO 🔥

Rodadas: {rodada}/15
Faltam: {faltam}
"""

    bot.edit_message_text(texto, GRUPO_ID, mensagem_grupo_id)

# ================= ANALISE =================

def analisar():
    global alerta_enviado

    if alerta_enviado:
        return

    total = len(numeros)
    restante = MAX_RODADAS - total

    pares = impares = 0
    count_A = count_B = 0

    for n in numeros:
        if n in grupo_A: count_A += 1
        if n in grupo_B: count_B += 1

        cor, par, altura = classificar(n)
        if par == "par": pares += 1
        if par == "impar": impares += 1

    # Estratégia A
    if total >= 10 and count_A == 0:
        alerta_enviado = True
        bot.send_message(GRUPO_ID, "🚨 ESTRATÉGIA A\nEntrar: 3-6-9")
        enviar_gestor(3)
        return

    # Estratégia B
    if total >= 10 and count_B == 0:
        alerta_enviado = True
        bot.send_message(GRUPO_ID, "🚨 ESTRATÉGIA B\nEntrar: 0-10")
        enviar_gestor(2)
        return

    # Contra tendência antecipada
    if pares > impares + restante:
        alerta_enviado = True
        bot.send_message(GRUPO_ID, "🏆 PAR venceu ciclo\nEntrar no ÍMPAR")
        enviar_gestor(18)

    elif impares > pares + restante:
        alerta_enviado = True
        bot.send_message(GRUPO_ID, "🏆 ÍMPAR venceu ciclo\nEntrar no PAR")
        enviar_gestor(18)

# ================= START =================

@bot.message_handler(commands=['start'])
def start(msg):

    if msg.from_user.id in ADMINS:
        bot.send_message(msg.chat.id, "🎯 PAINEL ADM SNIPER", reply_markup=criar_tabela())

    if msg.chat.id == GRUPO_ID:
        iniciar_painel_grupo()

# ================= RECEBER NUMERO =================

@bot.callback_query_handler(func=lambda call: True)
def receber(call):
    global numeros, alerta_enviado

    if call.from_user.id not in ADMINS:
        return

    numero = int(call.data)
    numeros.append(numero)

    texto_adm = f"""
🎯 PAINEL ADM ({len(numeros)}/15)

Sequência:
{numeros}
"""

    bot.edit_message_text(
        texto_adm,
        call.message.chat.id,
        call.message.message_id,
        reply_markup=criar_tabela()
    )

    atualizar_grupo()
    analisar()

    if len(numeros) == MAX_RODADAS:
        bot.send_message(GRUPO_ID, f"✅ CICLO FINALIZADO\n{numeros}")
        numeros = []
        alerta_enviado = False
        iniciar_painel_grupo()

print("🔥 SNIPER VIP 100% FUNCIONANDO 🔥")
bot.infinity_polling()
