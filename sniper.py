import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import os

TOKEN = os.getenv("TOKEN")
bot = telebot.TeleBot(TOKEN)

ADMINS = [8431121309]
GRUPO_ID = -1003629208122
MAX_RODADAS = 15

numeros = []
mensagem_painel = None
alerta_enviado = False
saldos = {}
aguardando_saldo = []

grupo_A = {3,6,9,13,16,19,23,26,29,33,36}
grupo_B = {19,15,32,0,26,3,35,12,28,8,25,10,5}
vermelhos = {1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36}

# ================= CLASSIFICAR =================

def classificar(numero):
    if numero == 0:
        return "verde", "zero", "zero"

    cor = "vermelho" if numero in vermelhos else "preto"
    par = "par" if numero % 2 == 0 else "impar"
    altura = "baixo" if numero <= 18 else "alto"

    return cor, par, altura

# ================= CRIAR TABELA ADM =================

def criar_tabela():
    markup = InlineKeyboardMarkup(row_width=6)
    botoes = []
    for i in range(37):
        botoes.append(InlineKeyboardButton(str(i), callback_data=str(i)))
    markup.add(*botoes)
    return markup

# ================= PAINEL GRUPO =================

def iniciar_painel():
    global mensagem_painel

    texto = """
🔥 SNIPER AO VIVO 🔥

Rodadas: 0/15
Faltam: 15

Aguardando números...
"""
    msg = bot.send_message(GRUPO_ID, texto)
    mensagem_painel = msg.message_id

def atualizar_painel():
    rodada = len(numeros)
    faltam = MAX_RODADAS - rodada

    texto = f"""
🔥 SNIPER AO VIVO 🔥

Rodadas: {rodada}/15
Faltam: {faltam}

Últimos números:
{numeros}
"""
    bot.edit_message_text(texto, GRUPO_ID, mensagem_painel)

# ================= GESTOR =================

def enviar_gestor(qtd_numeros):
    for user_id, saldo in saldos.items():

        aposta_base = 1
        total_entrada = qtd_numeros * aposta_base
        lucro = aposta_base * 36 - total_entrada
        meia_banca = saldo / 2
        banca_total = saldo

        texto = f"""
💰 GESTÃO DE BANCA

Saldo: ${saldo}

Entrada Normal:
Aposte $1 em cada número
Total investido: ${total_entrada}
Lucro possível: ${lucro}

Meia banca: ${meia_banca}
Banca total: ${banca_total}
"""
        bot.send_message(user_id, texto)

# ================= ANALISE =================

def analisar():
    global alerta_enviado

    if alerta_enviado:
        return

    total = len(numeros)

    count_A = sum(1 for n in numeros if n in grupo_A)
    count_B = sum(1 for n in numeros if n in grupo_B)

    pares = sum(1 for n in numeros if n != 0 and n % 2 == 0)
    impares = sum(1 for n in numeros if n % 2 == 1)

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

    # Tendência antecipada na 12ª
    if total == 12:
        if pares > impares:
            alerta_enviado = True
            bot.send_message(GRUPO_ID, "📊 Tendência PAR forte\nEntrar ÍMPAR")
            enviar_gestor(18)
        elif impares > pares:
            alerta_enviado = True
            bot.send_message(GRUPO_ID, "📊 Tendência ÍMPAR forte\nEntrar PAR")
            enviar_gestor(18)

# ================= START =================

@bot.message_handler(commands=['start'])
def start(msg):

    if msg.from_user.id in ADMINS:
        bot.send_message(msg.chat.id, "🎯 PAINEL ADM", reply_markup=criar_tabela())

    else:
        aguardando_saldo.append(msg.from_user.id)
        bot.send_message(msg.chat.id, "💰 Informe seu saldo atual:")

# ================= RECEBER SALDO =================

@bot.message_handler(func=lambda message: message.from_user.id in aguardando_saldo)
def receber_saldo(msg):
    try:
        saldo = float(msg.text)
        saldos[msg.from_user.id] = saldo
        aguardando_saldo.remove(msg.from_user.id)
        bot.send_message(msg.chat.id, "✅ Saldo registrado com sucesso!")
    except:
        bot.send_message(msg.chat.id, "Digite apenas números.")

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

    atualizar_painel()
    analisar()

    if len(numeros) == MAX_RODADAS:
        bot.send_message(GRUPO_ID, f"✅ CICLO FINALIZADO\n{numeros}")
        numeros = []
        alerta_enviado = False
        iniciar_painel()

# ================= INICIAR AUTOMATICO =================

print("🔥 SNIPER VIP 100% ONLINE 🔥")
iniciar_painel()
bot.infinity_polling()
