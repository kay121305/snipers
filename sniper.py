import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import os

TOKEN = os.getenv("TOKEN")
bot = telebot.TeleBot(TOKEN)

ADMINS = [8431121309]  # SEU ID

# ================= DADOS =================

historico = []

contador = {
    "preto": 0,
    "vermelho": 0,
    "zero": 0,
    "par": 0,
    "impar": 0,
    "alto": 0,
    "baixo": 0
}

vermelhos = {1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36}

# ================= FUNÇÕES =================

def analisar(numero):
    if numero == 0:
        contador["zero"] += 1
        return

    if numero in vermelhos:
        contador["vermelho"] += 1
    else:
        contador["preto"] += 1

    if numero % 2 == 0:
        contador["par"] += 1
    else:
        contador["impar"] += 1

    if numero >= 19:
        contador["alto"] += 1
    else:
        contador["baixo"] += 1

def placar_texto():
    ultimos = " - ".join(map(str, historico[-10:]))

    return f"""
🎰 $SNIPER$ AO VIVO

Últimos: {ultimos}

⚫ Preto: {contador['preto']}
🔴 Vermelho: {contador['vermelho']}
🟢 Zero: {contador['zero']}

🔢 Par: {contador['par']}
🔢 Ímpar: {contador['impar']}

⬆️ Alto: {contador['alto']}
⬇️ Baixo: {contador['baixo']}
"""

def resetar():
    historico.clear()
    for k in contador:
        contador[k] = 0

# ================= PAINEL =================

def painel():
    markup = InlineKeyboardMarkup(row_width=6)
    botoes = []
    for i in range(37):
        botoes.append(InlineKeyboardButton(str(i), callback_data=str(i)))
    markup.add(*botoes)
    return markup

# ================= START =================

@bot.message_handler(commands=['start'])
def start(message):
    if message.from_user.id in ADMINS:
        bot.send_message(
            message.chat.id,
            "🎰 $SNIPER$ PAINEL ADM ATIVO",
            reply_markup=painel()
        )
        bot.send_message(message.chat.id, placar_texto())
    else:
        bot.send_message(message.chat.id, "🎰 $SNIPER$ Sala VIP")

# ================= CLIQUE =================

@bot.callback_query_handler(func=lambda call: True)
def clicar(call):

    if call.from_user.id not in ADMINS:
        bot.answer_callback_query(call.id, "Somente ADM pode usar.")
        return

    numero = int(call.data)
    historico.append(numero)
    analisar(numero)

    bot.answer_callback_query(call.id, f"Número {numero} registrado")

    bot.send_message(call.message.chat.id, placar_texto())

    # Reset automático a cada 15
    if len(historico) >= 15:
        bot.send_message(call.message.chat.id, "📊 15 rodadas concluídas. Resetando ciclo.")
        resetar()

# ================= RODAR =================

print("SNIPER ONLINE")
bot.infinity_polling()
