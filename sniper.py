import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import os

TOKEN = os.getenv("TOKEN")
bot = telebot.TeleBot(TOKEN)

GRUPO_ID = -1003629208122
ADMIN_ID = 8431121309

# ================= CONFIG NUMEROS =================

vermelhos = {1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36}
pretos = {2,4,6,8,10,11,13,15,17,20,22,24,26,28,29,31,33,35}
altos = set(range(19,37))
baixos = set(range(1,19))

grupo_A = {3,6,9}
grupo_B = {0,10}

numeros = []
placar = {"par":0,"impar":0,"preto":0,"vermelho":0,"alto":0,"baixo":0}
banca = {}
entrada_ativa = None
alerta_enviado = False
painel_msg_id = None

# ================= TECLADO 0-36 =================

def teclado_numeros():
    markup = InlineKeyboardMarkup(row_width=6)
    botoes = []
    for i in range(37):
        botoes.append(InlineKeyboardButton(str(i), callback_data=str(i)))
    markup.add(*botoes)
    return markup

# ================= PLACAR =================

def resetar():
    global numeros, placar, entrada_ativa, alerta_enviado
    numeros = []
    placar = {"par":0,"impar":0,"preto":0,"vermelho":0,"alto":0,"baixo":0}
    entrada_ativa = None
    alerta_enviado = False

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

def texto_painel():
    return f"""
🎯 SNIPER VIP AO VIVO ({len(numeros)}/15)

⚫ Preto: {placar['preto']}
🔴 Vermelho: {placar['vermelho']}

🔵 Par: {placar['par']}
🟣 Ímpar: {placar['impar']}

⬆ Alto: {placar['alto']}
⬇ Baixo: {placar['baixo']}
"""

# ================= GESTOR =================

def enviar_gestor(qtd):
    if ADMIN_ID not in banca:
        return

    saldo = banca[ADMIN_ID]

    def calc(percent):
        valor = saldo * percent
        ficha = round(valor/qtd,2)
        ganho = round(ficha*36,2)
        lucro = round(ganho-valor,2)
        return ficha, ganho, lucro

    f1,g1,l1 = calc(0.24)
    f2,g2,l2 = calc(0.48)
    f3,g3,l3 = calc(1.0)

    bot.send_message(GRUPO_ID, f"""
💰 GESTÃO DE BANCA

🔹 Conservador
Ficha: R${f1}
Lucro: R${l1}

🔹 Médio
Ficha: R${f2}
Lucro: R${l2}

🔹 Agressivo
Ficha: R${f3}
Lucro: R${l3}
""")

# ================= ESTRATEGIAS =================

def verificar_estrategia(num):
    global entrada_ativa, alerta_enviado

    if entrada_ativa == "A" and num in grupo_A:
        bot.send_message(GRUPO_ID,"✅ GREEN ESTRATÉGIA A")
        entrada_ativa = None
        alerta_enviado = False
        return

    if entrada_ativa == "B" and num in grupo_B:
        bot.send_message(GRUPO_ID,"✅ GREEN ESTRATÉGIA B")
        entrada_ativa = None
        alerta_enviado = False
        return

    if len(numeros) >= 10 and not alerta_enviado:
        ultimos10 = numeros[-10:]

        if not any(n in grupo_A for n in ultimos10):
            entrada_ativa = "A"
            alerta_enviado = True
            bot.send_message(GRUPO_ID,
                f"🚨 ENTRAR AGORA\n\nApós o número: {num}\n\n🎯 Estratégia A\nEntrar: 3 - 6 - 9")
            enviar_gestor(3)

        elif not any(n in grupo_B for n in ultimos10):
            entrada_ativa = "B"
            alerta_enviado = True
            bot.send_message(GRUPO_ID,
                f"🚨 ENTRAR AGORA\n\nApós o número: {num}\n\n🎯 Estratégia B\nEntrar: 0 - 10")
            enviar_gestor(2)

# ================= TENDENCIA =================

def analisar_tendencia():
    if len(numeros) < 12:
        return

    if placar["par"] >= 8:
        nums = [n for n in range(37) if n % 2 == 1]
        bot.send_message(GRUPO_ID,f"📊 PAR forte\nEntrar ÍMPAR\n{nums}")

    if placar["impar"] >= 8:
        nums = [n for n in range(37) if n % 2 == 0]
        bot.send_message(GRUPO_ID,f"📊 ÍMPAR forte\nEntrar PAR\n{nums}")

# ================= START =================

@bot.message_handler(commands=['start'])
def start(msg):
    if msg.from_user.id != ADMIN_ID:
        bot.send_message(msg.chat.id,"🔒 Apenas admin controla.")
        return

    bot.send_message(msg.chat.id,"Digite o saldo da banca:")

@bot.message_handler(func=lambda m: m.from_user.id == ADMIN_ID and m.text.isdigit())
def salvar_banca(msg):
    banca[ADMIN_ID] = float(msg.text)

    global painel_msg_id
    painel = bot.send_message(GRUPO_ID, texto_painel(), reply_markup=teclado_numeros())
    painel_msg_id = painel.message_id

# ================= CLIQUE NUMERO =================

@bot.callback_query_handler(func=lambda call: True)
def clicar(call):
    global numeros

    if call.from_user.id != ADMIN_ID:
        return

    num = int(call.data)
    numeros.append(num)
    atualizar_placar(num)

    bot.edit_message_text(
        texto_painel(),
        GRUPO_ID,
        painel_msg_id,
        reply_markup=teclado_numeros()
    )

    verificar_estrategia(num)
    analisar_tendencia()

    if len(numeros) == 15:
        bot.send_message(GRUPO_ID,
            f"📈 RESULTADO 15 RODADAS\n\n"
            f"Par {placar['par']} x {placar['impar']} Ímpar\n"
            f"Preto {placar['preto']} x {placar['vermelho']} Vermelho\n"
            f"Alto {placar['alto']} x {placar['baixo']} Baixo")
        resetar()

print("🔥 SNIPER VIP 100% ONLINE 🔥")
bot.infinity_polling()
