import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import os

TOKEN = os.getenv("TOKEN")
bot = telebot.TeleBot(TOKEN)

GRUPO_ID = -1003629208122
ADMIN_ID = 8431121309

# ================= CONFIGURAÇÕES =================

vermelhos = {1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36}
pretos = {2,4,6,8,10,11,13,15,17,20,22,24,26,28,29,31,33,35}
altos = set(range(19,37))
baixos = set(range(1,19))

grupo_A = {3,6,9}
grupo_B = {0,10}

numeros = []
placar = {}
banca = 0
entrada_ativa = None
alerta_enviado = False
painel_id = None
tendencia_enviada = False

# ================= FUNÇÕES BASE =================

def resetar_tudo():
    global numeros, placar, entrada_ativa, alerta_enviado, tendencia_enviada
    numeros = []
    placar = {"par":0,"impar":0,"preto":0,"vermelho":0,"alto":0,"baixo":0}
    entrada_ativa = None
    alerta_enviado = False
    tendencia_enviada = False

resetar_tudo()

def teclado():
    kb = InlineKeyboardMarkup(row_width=6)
    botoes = [InlineKeyboardButton(str(i), callback_data=str(i)) for i in range(37)]
    kb.add(*botoes)
    return kb

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

⚫ Preto: {placar['preto']} | 🔴 Vermelho: {placar['vermelho']}
🔵 Par: {placar['par']} | 🟣 Ímpar: {placar['impar']}
⬆ Alto: {placar['alto']} | ⬇ Baixo: {placar['baixo']}
"""

# ================= GESTOR =================

def enviar_gestor(qtd):
    global banca
    if banca <= 0:
        return

    def calc(ficha):
        total = ficha * qtd
        if total > banca:
            ficha = banca/qtd
            total = banca
        ganho = ficha * 36
        lucro = ganho - total
        return round(ficha,2), round(lucro,2)

    f1,l1 = calc(1)
    f2,l2 = calc(2)
    f3,l3 = calc(4)

    bot.send_message(GRUPO_ID,f"""
💰 GESTÃO DE BANCA

🔹 Conservador
Ficha: R${f1}
Lucro: R${l1}

🔹 Médio
Ficha: R${f2}
Lucro: R${l2}

🔹 Máximo
Ficha: R${f3}
Lucro: R${l3}
""")

# ================= TENDÊNCIA COMBINADA =================

def analisar_tendencia():
    global tendencia_enviada

    if len(numeros) < 12 or tendencia_enviada:
        return

    if placar["preto"] >= 8 or placar["vermelho"] >= 8:
        tendencia_enviada = True

        cor_dominante = "preto" if placar["preto"] >= placar["vermelho"] else "vermelho"
        par_dominante = "par" if placar["par"] >= placar["impar"] else "impar"
        altura_dominante = "alto" if placar["alto"] >= placar["baixo"] else "baixo"

        numeros_filtrados = []

        for n in range(1,37):

            cond_cor = (n in vermelhos) if cor_dominante == "preto" else (n in pretos)
            cond_par = (n % 2 == 1) if par_dominante == "par" else (n % 2 == 0)
            cond_altura = (n in baixos) if altura_dominante == "alto" else (n in altos)

            if cond_cor and cond_par and cond_altura:
                numeros_filtrados.append(n)

        bot.send_message(GRUPO_ID,
            f"""🔥 TENDÊNCIA DETECTADA

Domínio identificado.
Entrar nos números:

{sorted(numeros_filtrados)}
""")

# ================= ESTRATÉGIAS =================

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

# ================= COMANDOS =================

@bot.message_handler(commands=['start'])
def start(msg):
    if msg.from_user.id != ADMIN_ID:
        bot.send_message(msg.chat.id,"🔒 Apenas admin.")
        return
    bot.send_message(msg.chat.id,"Digite o saldo da banca:")

@bot.message_handler(commands=['reset'])
def reset_cmd(msg):
    if msg.from_user.id == ADMIN_ID:
        resetar_tudo()
        bot.send_message(GRUPO_ID,"♻ Rodadas resetadas.")

@bot.message_handler(commands=['teste'])
def teste_gestor(msg):
    if msg.from_user.id == ADMIN_ID:
        enviar_gestor(3)

@bot.message_handler(func=lambda m: m.from_user.id == ADMIN_ID and m.text.isdigit())
def salvar_banca(msg):
    global banca, painel_id
    banca = float(msg.text)
    painel = bot.send_message(GRUPO_ID, texto_painel(), reply_markup=teclado())
    painel_id = painel.message_id

# ================= CLIQUES =================

@bot.callback_query_handler(func=lambda call: True)
def clique(call):
    global numeros

    if call.from_user.id != ADMIN_ID:
        return

    num = int(call.data)
    numeros.append(num)
    atualizar_placar(num)

    bot.edit_message_text(
        texto_painel(),
        GRUPO_ID,
        painel_id,
        reply_markup=teclado()
    )

    verificar_estrategia(num)
    analisar_tendencia()

    if len(numeros) == 15:
        bot.send_message(GRUPO_ID,
            f"""📈 RESULTADO DAS 15 RODADAS

Par {placar['par']} x {placar['impar']} Ímpar
Preto {placar['preto']} x {placar['vermelho']} Vermelho
Alto {placar['alto']} x {placar['baixo']} Baixo
""")
        resetar_tudo()

print("🔥 SNIPER VIP DEFINITIVO ONLINE 🔥")
bot.infinity_polling()
