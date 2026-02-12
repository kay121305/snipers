import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import os

TOKEN = os.getenv("TOKEN")
bot = telebot.TeleBot(TOKEN)

ADMINS = [8431121309]

MAX_RODADAS = 15
numeros = []
alerta_enviado = False

vermelhos = {1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36}
pretos = {2,4,6,8,10,11,13,15,17,20,22,24,26,28,29,31,33,35}

# ================= CLASSIFICAR =================

def classificar(numero):
    if numero == 0:
        return None

    cor = "vermelho" if numero in vermelhos else "preto"
    par = "par" if numero % 2 == 0 else "impar"
    altura = "baixo" if numero <= 18 else "alto"

    return cor, par, altura

# ================= TABELA =================

def criar_tabela():
    markup = InlineKeyboardMarkup(row_width=6)
    botoes = []
    for i in range(37):
        botoes.append(InlineKeyboardButton(str(i), callback_data=str(i)))
    markup.add(*botoes)
    return markup

# ================= GERAR NUMEROS FILTRADOS =================

def gerar_numeros(cor, par, altura):
    lista = []
    for n in range(1,37):
        c = classificar(n)
        if not c:
            continue
        if c[0]==cor and c[1]==par and c[2]==altura:
            lista.append(n)
    return lista

# ================= ANALISE INTELIGENTE =================

def analisar(chat_id):
    global alerta_enviado

    total = len(numeros)
    restante = MAX_RODADAS - total

    pares = impares = verm = pret = altos = baixos = 0

    for n in numeros:
        c = classificar(n)
        if not c:
            continue
        cor, par, altura = c
        if par == "par": pares += 1
        if par == "impar": impares += 1
        if cor == "vermelho": verm += 1
        if cor == "preto": pret += 1
        if altura == "alto": altos += 1
        if altura == "baixo": baixos += 1

    if alerta_enviado:
        return

    def venceu(a, b):
        return a > b + restante

    # Verifica vencedor
    vencedor = None
    if venceu(pares, impares): vencedor = ("par","vermelho" if verm>pret else "preto","alto" if altos>baixos else "baixo")
    elif venceu(impares, pares): vencedor = ("impar","vermelho" if verm>pret else "preto","alto" if altos>baixos else "baixo")

    if vencedor:
        alerta_enviado = True

        par_venc, cor_venc, alt_venc = vencedor

        # CONTRÁRIO
        par_c = "impar" if par_venc=="par" else "par"
        cor_c = "preto" if cor_venc=="vermelho" else "vermelho"
        alt_c = "baixo" if alt_venc=="alto" else "alto"

        numeros_sinal = gerar_numeros(cor_c, par_c, alt_c)

        texto = f"""
🏆 {par_venc.upper()} JÁ VENCEU O CICLO

🎯 ENTRAR NO CONTRÁRIO:

{par_c.upper()} + {cor_c.upper()} + {alt_c.upper()}

NÚMEROS:
{numeros_sinal}
"""

        bot.send_message(chat_id, texto)

# ================= RELATORIO =================

def relatorio_final(chat_id):
    texto = f"""
📊 CICLO ENCERRADO (15 RODADAS)

Sequência:
{numeros}
"""
    bot.send_message(chat_id, texto)

# ================= START =================

@bot.message_handler(commands=['start'])
def start(msg):
    if msg.from_user.id in ADMINS:
        bot.send_message(msg.chat.id, "🎯 PAINEL ADM SNIPER 🎯", reply_markup=criar_tabela())
    else:
        bot.send_message(msg.chat.id, "🔥 SALA VIP $SNIPER$ 🔥")

# ================= RECEBER =================

@bot.callback_query_handler(func=lambda call: True)
def receber(call):
    global numeros, alerta_enviado

    if call.from_user.id not in ADMINS:
        return

    numero = int(call.data)
    numeros.append(numero)

    texto = f"🎯 AO VIVO ({len(numeros)}/15)\n"
    texto += " - ".join(map(str, numeros))

    bot.edit_message_text(
        texto,
        call.message.chat.id,
        call.message.message_id,
        reply_markup=criar_tabela()
    )

    analisar(call.message.chat.id)

    if len(numeros) == MAX_RODADAS:
        relatorio_final(call.message.chat.id)
        numeros = []
        alerta_enviado = False

print("SNIPER CONTRA-TENDENCIA ONLINE 🚀")
bot.infinity_polling()
