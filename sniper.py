import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import os

TOKEN = os.getenv("TOKEN")
bot = telebot.TeleBot(TOKEN)

ADMINS = [8431121309]

GRUPO_ID = None  # depois podemos fixar aqui

MAX_RODADAS = 15
numeros = []
alerta_enviado = False
saldos = {}

grupo_A = {3,6,9,13,16,19,23,26,29,33,36}
grupo_B = {19,15,32,0,26,3,35,12,28,8,25,10,5}

vermelhos = {1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36}
pretos = {2,4,6,8,10,11,13,15,17,20,22,24,26,28,29,31,33,35}

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

def enviar_gestor(chat_id, qtd_numeros):
    if chat_id not in saldos:
        return

    saldo = saldos[chat_id]
    ficha = 1
    total = ficha * qtd_numeros
    retorno = 36 * ficha
    lucro = retorno - total

    texto = f"""
💰 GESTÃO DE BANCA

Saldo: ${saldo}

Entrada Normal:
Valor por número: $1
Total investido: ${total}
Lucro possível: ${lucro}

1/2 banca: ${round(saldo/2,2)}
Banca total: ${saldo}
"""
    bot.send_message(chat_id, texto)

# ================= START =================

@bot.message_handler(commands=['start'])
def start(msg):

    if msg.chat.type in ["group", "supergroup"]:
        global GRUPO_ID
        GRUPO_ID = msg.chat.id

    if msg.from_user.id in ADMINS:
        bot.send_message(msg.chat.id, "🎯 PAINEL ADM $SNIPER$", reply_markup=criar_tabela())
    else:
        bot.send_message(msg.chat.id, "🔥 Você está na Sala VIP $SNIPER$ 🔥")

# ================= SALDO =================

@bot.message_handler(commands=['saldo'])
def saldo(msg):
    try:
        valor = float(msg.text.split()[1])
        saldos[msg.chat.id] = valor
        bot.send_message(msg.chat.id, f"Saldo registrado: ${valor}")
    except:
        bot.send_message(msg.chat.id, "Use: /saldo 50")

# ================= ATUALIZAR GRUPO =================

def atualizar_grupo():
    if GRUPO_ID is None:
        return

    rodada = len(numeros)
    faltam = MAX_RODADAS - rodada

    texto = f"""
🔴 AO VIVO $SNIPER$

Rodadas: {rodada}/15
Faltam: {faltam}
"""

    bot.send_message(GRUPO_ID, texto)

# ================= ANALISE =================

def analisar(chat_id):
    global alerta_enviado

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

    if alerta_enviado:
        return

    # Estratégia A
    if total >= 10 and count_A == 0:
        alerta_enviado = True
        bot.send_message(chat_id, "🚨 ESTRATÉGIA A\nEntrar 3-6-9")
        enviar_gestor(chat_id, 3)
        return

    # Estratégia B
    if total >= 10 and count_B == 0:
        alerta_enviado = True
        bot.send_message(chat_id, "🚨 ESTRATÉGIA B\nEntrar 0-10")
        enviar_gestor(chat_id, 2)
        return

    # Contra tendência
    if pares > impares + restante:
        alerta_enviado = True
        bot.send_message(chat_id, "🏆 PAR venceu ciclo\nEntrar no ÍMPAR")
        enviar_gestor(chat_id, 18)

    elif impares > pares + restante:
        alerta_enviado = True
        bot.send_message(chat_id, "🏆 ÍMPAR venceu ciclo\nEntrar no PAR")
        enviar_gestor(chat_id, 18)

# ================= RECEBER NUMERO =================

@bot.callback_query_handler(func=lambda call: True)
def receber(call):
    global numeros, alerta_enviado

    if call.from_user.id not in ADMINS:
        return

    numero = int(call.data)
    numeros.append(numero)

    texto = f"""
🎯 PAINEL ADM ({len(numeros)}/15)

Sequência:
{numeros}
"""

    bot.edit_message_text(
        texto,
        call.message.chat.id,
        call.message.message_id,
        reply_markup=criar_tabela()
    )

    atualizar_grupo()
    analisar(call.message.chat.id)

    if len(numeros) == MAX_RODADAS:
        if GRUPO_ID:
            bot.send_message(GRUPO_ID, f"✅ CICLO FINALIZADO\n{numeros}")

        numeros = []
        alerta_enviado = False

print("🔥 SNIPER VIP COMPLETO ONLINE 🔥")
bot.infinity_polling()
