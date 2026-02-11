import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import os

TOKEN = os.getenv("TOKEN")
bot = telebot.TeleBot(TOKEN)

# ================= CONFIG =================

ADMINS = [8535416972]  # coloque seu ID

grupo_A = {3,6,9,13,16,19,23,26,29,33,36}
grupo_B = {19,15,32,0,26,3,35,12,28,8,25,10,5}

historico = []
contador = {
    "preto":0,"vermelho":0,"zero":0,
    "par":0,"impar":0,
    "alto":0,"baixo":0
}

bancas = {}

# ================= CORES =================

vermelhos = {1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36}

# ================= FUNÇÕES =================

def analisar_numero(num):
    if num == 0:
        contador["zero"] += 1
    else:
        if num in vermelhos:
            contador["vermelho"] += 1
        else:
            contador["preto"] += 1

        if num % 2 == 0:
            contador["par"] += 1
        else:
            contador["impar"] += 1

        if num >= 19:
            contador["alto"] += 1
        else:
            contador["baixo"] += 1


def verificar_estrategias(chat_id):
    if len(historico) >= 10:
        ultimos = historico[-10:]

        if not any(n in grupo_A for n in ultimos):
            bot.send_message(chat_id,"🔥 ENTRADA A\nApostar: 3 - 6 - 9")

        if not any(n in grupo_B for n in ultimos):
            bot.send_message(chat_id,"🔥 ENTRADA B\nApostar Grupo B")


def verificar_tendencia(chat_id):
    if len(historico) >= 12:

        if contador["par"] - contador["impar"] >= 4:
            tipo = "PAR"
        elif contador["impar"] - contador["par"] >= 4:
            tipo = "ÍMPAR"
        else:
            return

        if contador["preto"] - contador["vermelho"] >= 4:
            cor = "PRETO"
        elif contador["vermelho"] - contador["preto"] >= 4:
            cor = "VERMELHO"
        else:
            return

        if contador["alto"] - contador["baixo"] >= 4:
            altura = "ALTO"
        elif contador["baixo"] - contador["alto"] >= 4:
            altura = "BAIXO"
        else:
            return

        bot.send_message(chat_id,f"🔥 TENDÊNCIA\n{tipo} + {cor} + {altura}")


def relatorio(chat_id):
    bot.send_message(chat_id,f"""
📊 RELATÓRIO 15 RODADAS

Preto: {contador['preto']}
Vermelho: {contador['vermelho']}
Zero: {contador['zero']}

Par: {contador['par']}
Ímpar: {contador['impar']}

Alto: {contador['alto']}
Baixo: {contador['baixo']}
""")

# ================= PAINEL =================

def painel():
    markup = InlineKeyboardMarkup(row_width=6)
    botoes = []
    for i in range(37):
        botoes.append(InlineKeyboardButton(str(i), callback_data=str(i)))
    markup.add(*botoes)
    return markup

# ================= COMANDOS =================

@bot.message_handler(commands=['start'])
def start(message):
    if message.from_user.id in ADMINS:
        bot.send_message(message.chat.id,"🎰 $NIPER$ ATIVO", reply_markup=painel())
    else:
        bot.send_message(message.chat.id,"🎰 $NIPER$ Sala VIP")

@bot.message_handler(commands=['banca'])
def banca(message):
    try:
        valor = float(message.text.split()[1])
        bancas[message.from_user.id] = valor
        bot.send_message(message.chat.id,f"💰 Banca atualizada: {valor}")
    except:
        bot.send_message(message.chat.id,"Use /banca 50")

# ================= CLIQUE =================

@bot.callback_query_handler(func=lambda call: True)
def clicar(call):
    if call.from_user.id not in ADMINS:
        return

    num = int(call.data)
    historico.append(num)

    analisar_numero(num)

    bot.answer_callback_query(call.id,f"Número {num} registrado")

    verificar_estrategias(call.message.chat.id)
    verificar_tendencia(call.message.chat.id)

    if len(historico) == 15:
        relatorio(call.message.chat.id)
        historico.clear()
        for k in contador:
            contador[k]=0

# ================= START BOT =================

bot.infinity_polling()
