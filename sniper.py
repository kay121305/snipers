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
aguardando_saldo = set()

vermelhos = {1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36}

grupo_A = {3,6,9,13,16,19,23,26,29,33,36}
grupo_B = {19,15,32,0,26,3,35,12,28,8,25,10,5}

# ================= CLASSIFICAR =================

def classificar(numero):
    if numero == 0:
        return "Verde", "-", "-"

    cor = "Vermelho" if numero in vermelhos else "Preto"
    paridade = "Par" if numero % 2 == 0 else "Ímpar"
    altura = "Baixo" if numero <= 18 else "Alto"

    return cor, paridade, altura

# ================= TABELA ADM =================

def criar_tabela():
    markup = InlineKeyboardMarkup(row_width=6)
    botoes = [InlineKeyboardButton(str(i), callback_data=str(i)) for i in range(37)]
    markup.add(*botoes)
    return markup

# ================= PAINEL GRUPO =================

def iniciar_painel():
    global mensagem_painel
    texto = "🔥 SNIPER AO VIVO 🔥\n\nRodadas: 0/15\nFaltam: 15"
    msg = bot.send_message(GRUPO_ID, texto)
    mensagem_painel = msg.message_id

def atualizar_painel():
    rodada = len(numeros)
    faltam = MAX_RODADAS - rodada

    texto = f"🔥 SNIPER AO VIVO 🔥\n\nRodadas: {rodada}/15\nFaltam: {faltam}"
    bot.edit_message_text(texto, GRUPO_ID, mensagem_painel)

# ================= GESTOR =================

def enviar_gestor(qtd_numeros):
    for user_id, saldo in saldos.items():

        valor_ficha = 1
        total = qtd_numeros * valor_ficha
        retorno = valor_ficha * 36
        lucro = retorno - total

        texto = f"""
💰 GESTÃO DE BANCA

Saldo: ${saldo}

Entrada:
${valor_ficha} por número
Total investido: ${total}

Retorno possível: ${retorno}
Lucro líquido: ${lucro}
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

    if total >= 10 and count_A == 0:
        alerta_enviado = True
        bot.send_message(GRUPO_ID, "🚨 Estratégia A: Entrar 3-6-9")
        enviar_gestor(3)

    elif total >= 10 and count_B == 0:
        alerta_enviado = True
        bot.send_message(GRUPO_ID, "🚨 Estratégia B: Entrar 0-10")
        enviar_gestor(2)

# ================= START =================

@bot.message_handler(commands=['start'])
def start(msg):

    if msg.from_user.id in ADMINS:
        bot.send_message(msg.chat.id, "🎯 PAINEL ADM", reply_markup=criar_tabela())

    else:
        aguardando_saldo.add(msg.from_user.id)
        bot.send_message(msg.chat.id, "💰 Informe seu saldo atual:")

# ================= RECEBER SALDO =================

@bot.message_handler(func=lambda m: m.from_user.id in aguardando_saldo)
def receber_saldo(msg):
    try:
        saldo = float(msg.text)
        saldos[msg.from_user.id] = saldo
        aguardando_saldo.remove(msg.from_user.id)
        bot.send_message(msg.chat.id, "✅ Saldo salvo com sucesso!")
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

    # Contadores
    pretos = verm = pares = impares = altos = baixos = 0

    for n in numeros:
        cor, paridade, altura = classificar(n)
        if cor == "Preto": pretos += 1
        if cor == "Vermelho": verm += 1
        if paridade == "Par": pares += 1
        if paridade == "Ímpar": impares += 1
        if altura == "Alto": altos += 1
        if altura == "Baixo": baixos += 1

    cor, paridade, altura = classificar(numero)

    texto_adm = f"""
🎯 PAINEL ADM ({len(numeros)}/15)

Número: {numero}
Cor: {cor}
Paridade: {paridade}
Altura: {altura}

📊 PLACAR:
Preto: {pretos}
Vermelho: {verm}
Par: {pares}
Ímpar: {impares}
Alto: {altos}
Baixo: {baixos}
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

# ================= INICIAR =================

print("🔥 SNIPER VIP ONLINE 🔥")
iniciar_painel()
bot.infinity_polling()
