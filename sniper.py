# ============================================================
# 🔥 ROLETTE SNIPER VIP IA + HEATMAP + MESA REAL 🔥
# ============================================================

import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import os
import statistics
import math
from collections import defaultdict

TOKEN = os.getenv("TOKEN")
bot = telebot.TeleBot(TOKEN)

GRUPO_ID = -1003629208122
ADMIN_ID = 8431121309

CICLO_MAX = 15
MAX_GALES = 2
LIMPEZA_CICLOS = 2

# ============================================================
# CORES
# ============================================================

VERMELHOS = {1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36}
PRETOS = {2,4,6,8,10,11,13,15,17,20,22,24,26,28,29,31,33,35}

# ============================================================
# GRUPOS
# ============================================================

GRUPO_A = {3,6,9,13,16,19,23,26,29,33,36}
GRUPO_B = {19,15,32,0,26,3,35,12,28,8,23,10,5}

# ============================================================
# ESTADO
# ============================================================

numeros = []
placar = defaultdict(int)
markov = defaultdict(lambda: defaultdict(int))

indice_ciclo = 0
ciclos_total = 0

entrada_ativa = False
grupo_entrada = None
nome_jogada = ""
gales = 0

greens = 0
losses = 0

painel_id = None
mensagens_ids = []

numero_temp = None
aguardando_confirmacao = False

# ============================================================
# REGISTRAR MSG
# ============================================================

def registrar_msg(msg):
    mensagens_ids.append(msg.message_id)


# ============================================================
# LIMPAR MSG
# ============================================================

def limpar_mensagens():

    global mensagens_ids

    for mid in mensagens_ids:
        try:
            bot.delete_message(GRUPO_ID, mid)
        except:
            pass

    mensagens_ids.clear()


# ============================================================
# VARIÂNCIA
# ============================================================

def calcular_variancia():

    if len(numeros) < 2:
        return 0,0

    var = statistics.variance(numeros)
    desvio = math.sqrt(var)

    return round(var,2), round(desvio,2)


# ============================================================
# IA
# ============================================================

def atualizar_markov():

    if len(numeros) < 2:
        return

    a = numeros[-2]
    b = numeros[-1]

    markov[a][b] += 1


def prever_ia():

    if not numeros:
        return {}

    ultimo = numeros[-1]

    trans = markov[ultimo]

    total = sum(trans.values()) + 37

    probs = {}

    for n in range(37):
        probs[n] = (trans.get(n,0) + 1) / total

    return probs


# ============================================================
# HEATMAP
# ============================================================

def heatmap():

    freq = defaultdict(int)

    base = numeros[-30:]

    for n in base:
        freq[n] += 1

    txt = "🔥 HeatMap Últimas 30:\n"

    ranking = sorted(freq.items(), key=lambda x: x[1], reverse=True)[:6]

    for n,c in ranking:

        if c >= 4:
            emoji = "🟥🟥"
        elif c == 3:
            emoji = "🟥"
        elif c == 2:
            emoji = "🟧"
        elif c == 1:
            emoji = "🟨"
        else:
            emoji = "🟩"

        txt += f"{emoji} {n}\n"

    return txt


# ============================================================
# PLACAR
# ============================================================

def atualizar_placar(num):

    if num == 0:
        return

    if num % 2 == 0:
        placar["par"] += 1
    else:
        placar["impar"] += 1

    if num in PRETOS:
        placar["preto"] += 1

    if num in VERMELHOS:
        placar["vermelho"] += 1


# ============================================================
# TECLADO MESA REAL
# ============================================================

def teclado():

    kb = InlineKeyboardMarkup()

    linhas = [
        [3,6,9,12,15,18,21,24,27,30,33,36],
        [2,5,8,11,14,17,20,23,26,29,32,35],
        [1,4,7,10,13,16,19,22,25,28,31,34]
    ]

    for linha in linhas:

        botoes = []

        for n in linha:

            if n in PRETOS:
                cor = "⚫"
            else:
                cor = "🔴"

            botoes.append(
                InlineKeyboardButton(
                    f"{n}{cor}",
                    callback_data=f"num_{n}"
                )
            )

        kb.row(*botoes)

    kb.row(
        InlineKeyboardButton("0🟢", callback_data="num_0")
    )

    return kb


# ============================================================
# CONFIRMAÇÃO
# ============================================================

def teclado_confirmacao():

    kb = InlineKeyboardMarkup()

    kb.add(
        InlineKeyboardButton("✅ Confirmar", callback_data="confirmar"),
        InlineKeyboardButton("❌ Cancelar", callback_data="cancelar")
    )

    return kb


# ============================================================
# PAINEL
# ============================================================

def painel_texto():

    var, desvio = calcular_variancia()

    top = sorted(
        prever_ia().items(),
        key=lambda x: x[1],
        reverse=True
    )[:5]

    ia_txt = ""

    for n,p in top:
        ia_txt += f"{n}:{round(p*100,1)}% "

    return f"""
🎯 SNIPER VIP IA

Ciclo {indice_ciclo}/{CICLO_MAX}
Ciclos {ciclos_total}

📊 Var {var} | Desv {desvio}

🤖 IA:
{ia_txt}

{heatmap()}

✅ {greens} ❌ {losses}
"""


# ============================================================
# PROB MSG
# ============================================================

def mensagem_prob(num):

    top = sorted(
        prever_ia().items(),
        key=lambda x: x[1],
        reverse=True
    )[:5]

    txt = f"🎯 Número {num}\n\n🤖 Probabilidades:\n"

    for n,p in top:
        txt += f"{n} → {round(p*100,2)}%\n"

    return txt


# ============================================================
# SINAL
# ============================================================

def disparar_sinal(grupo, nome):

    global entrada_ativa, grupo_entrada, nome_jogada, gales

    entrada_ativa = True
    grupo_entrada = grupo
    nome_jogada = nome
    gales = 0

    msg = bot.send_message(
        GRUPO_ID,
        f"""
🚨 ENTRADA {nome}

Números:
{sorted(grupo)}

Gales {MAX_GALES}
"""
    )

    registrar_msg(msg)


# ============================================================
# VERIFICAR
# ============================================================

def verificar_sinais():

    if len(numeros) < 10:
        return

    ultimos = numeros[-10:]

    if not any(n in GRUPO_A for n in ultimos):
        disparar_sinal(GRUPO_A,"DG du GRAL")

    elif not any(n in GRUPO_B for n in ultimos):
        disparar_sinal(GRUPO_B,"Makako777")


# ============================================================
# RESUMO
# ============================================================

def resumo_ciclo():

    global ciclos_total, indice_ciclo

    ciclos_total += 1
    indice_ciclo = 0

    msg = bot.send_message(
        GRUPO_ID,
        f"""
📊 FIM CICLO

Greens {greens}
Loss {losses}
"""
    )

    registrar_msg(msg)

    if ciclos_total % LIMPEZA_CICLOS == 0:
        limpar_mensagens()


# ============================================================
# START
# ============================================================

@bot.message_handler(commands=["start"])
def start(msg):

    if msg.from_user.id != ADMIN_ID:
        return

    painel = bot.send_message(
        GRUPO_ID,
        painel_texto(),
        reply_markup=teclado()
    )

    global painel_id
    painel_id = painel.message_id


# ============================================================
# CALLBACK
# ============================================================

@bot.callback_query_handler(func=lambda call: True)
def callbacks(call):

    global numero_temp, aguardando_confirmacao
    global indice_ciclo, entrada_ativa, gales
    global greens, losses

    if call.from_user.id != ADMIN_ID:
        return

    data = call.data

    if data.startswith("num_"):

        numero_temp = int(data.split("_")[1])
        aguardando_confirmacao = True

        msg = bot.send_message(
            GRUPO_ID,
            mensagem_prob(numero_temp),
            reply_markup=teclado_confirmacao()
        )

        registrar_msg(msg)
        return

    if data == "cancelar":
        aguardando_confirmacao = False
        return

    if data == "confirmar":

        if not aguardando_confirmacao:
            return

        num = numero_temp
        aguardando_confirmacao = False

        numeros.append(num)
        atualizar_placar(num)
        atualizar_markov()

        indice_ciclo += 1

        bot.edit_message_text(
            painel_texto(),
            GRUPO_ID,
            painel_id,
            reply_markup=teclado()
        )

        # ENTRADA
        if entrada_ativa:

            if num in grupo_entrada:
                greens += 1
                entrada_ativa = False
                gales = 0
                bot.send_message(GRUPO_ID,"✅ GREEN")

            else:
                gales += 1

                if gales > MAX_GALES:
                    losses += 1
                    entrada_ativa = False
                    gales = 0
                    bot.send_message(GRUPO_ID,"❌ LOSS")

        verificar_sinais()

        if indice_ciclo >= CICLO_MAX:
            resumo_ciclo()


# ============================================================
# RUN
# ============================================================

print("🔥 BOT VIP IA HEATMAP EXECUTANDO 🔥")

bot.infinity_polling()
