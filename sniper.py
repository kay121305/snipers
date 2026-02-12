import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import os

TOKEN = os.getenv("TOKEN")
bot = telebot.TeleBot(TOKEN)

# ================= CONFIG =================
GRUPO_ID = -1003629208122  # ID do grupo VIP
ADMIN_ID = 8431121309       # Seu ID

# ===== NUMEROS =====
vermelhos = {1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36}
pretos = {2,4,6,8,10,11,13,15,17,20,22,24,26,28,29,31,33,35}
altos = set(range(19,37))
baixos = set(range(1,19))

# ===== ESTRATEGIAS =====
grupo_A = {3,6,9,13,16,19,23,26,29}
grupo_B = {19,15,32,0,26,3,35,12,28,8,23,10,5}

# ===== VARIAVEIS =====
numeros = []
placar = {"par":0,"impar":0,"preto":0,"vermelho":0,"alto":0,"baixo":0}
painel_id = None

entrada_ativa = None
grupo_entrada = None
gales = 0
numero_alerta = None

tendencia_ativa = False
numeros_tendencia = []
rodadas_tendencia = 0

banca = 0
aguardando_banca = False

# ================= RESET =================
def resetar():
    global numeros, placar, entrada_ativa, gales
    global numero_alerta, tendencia_ativa, rodadas_tendencia

    numeros.clear()
    placar.update({"par":0,"impar":0,"preto":0,"vermelho":0,"alto":0,"baixo":0})
    entrada_ativa = None
    gales = 0
    numero_alerta = None
    tendencia_ativa = False
    rodadas_tendencia = 0

# ================= TECLADO =================
def teclado():
    kb = InlineKeyboardMarkup(row_width=6)
    botoes = [InlineKeyboardButton(str(i), callback_data=str(i)) for i in range(37)]
    kb.add(*botoes)
    return kb

# ================= PAINEL =================
def painel_texto():
    return f"""
🎯 SNIPER VIP ({len(numeros)}/15)

⚫ Preto: {placar['preto']} | 🔴 Vermelho: {placar['vermelho']}
🔵 Par: {placar['par']} | 🟣 Ímpar: {placar['impar']}
⬆ Alto: {placar['alto']} | ⬇ Baixo: {placar['baixo']}
"""

# ================= ATUALIZA PLACAR =================
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

# ================= GESTOR =================
def enviar_gestor(numeros_aposta):
    if banca <= 0:
        return

    conservador = round(banca * 0.02,2)
    medio = round(banca * 0.05,2)
    agressivo = round(banca * 0.10,2)

    bot.send_message(GRUPO_ID,
f"""💰 GESTÃO DE BANCA

Entrada: {sorted(numeros_aposta)}

🔹 Conservador: R${conservador} por ficha
🔸 Médio: R${medio} por ficha
🔺 Agressivo: R${agressivo} por ficha
""")

# ================= ESTRATEGIAS =================
def verificar_estrategias(num):
    global entrada_ativa, gales, numero_alerta, grupo_entrada

    if entrada_ativa:
        if num in grupo_entrada:
            bot.send_message(GRUPO_ID,f"✅ GREEN no número {num}")
            entrada_ativa = None
            gales = 0
            return

        gales += 1
        if gales < 3:
            bot.send_message(GRUPO_ID,f"⚠ Gale {gales}")
        else:
            bot.send_message(GRUPO_ID,"❌ LOSS — Próxima entrada")
            entrada_ativa = None
            gales = 0
        return

    if len(numeros) >= 10:
        ultimos10 = numeros[-10:]
        if not any(n in grupo_A for n in ultimos10):
            entrada_ativa = True
            grupo_entrada = grupo_A
            numero_alerta = num
            gales = 0

            bot.send_message(GRUPO_ID,
f"""🚨 SINAL ESTRATÉGIA A

Após o número: {numero_alerta}

Entrar nos números: {sorted(grupo_A)}
Até 3 Gales
""")
            enviar_gestor(grupo_A)

        elif not any(n in grupo_B for n in ultimos10):
            entrada_ativa = True
            grupo_entrada = grupo_B
            numero_alerta = num
            gales = 0

            bot.send_message(GRUPO_ID,
f"""🚨 SINAL ESTRATÉGIA B

Após o número: {numero_alerta}

Entrar nos números: {sorted(grupo_B)}
Até 3 Gales
""")
            enviar_gestor(grupo_B)

# ================= TENDÊNCIA =================
def analisar_tendencia(num):
    global tendencia_ativa, numeros_tendencia, rodadas_tendencia

    if tendencia_ativa:
        rodadas_tendencia += 1
        if num in numeros_tendencia:
            bot.send_message(GRUPO_ID,f"✅ GREEN Tendência no número {num}")
            tendencia_ativa = False
            return
        if rodadas_tendencia >= 3:
            bot.send_message(GRUPO_ID,"❌ LOSS Tendência")
            tendencia_ativa = False
        return

    if placar["par"] >= 8 or placar["preto"] >= 6 or placar["alto"] >= 7:
        tendencia_ativa = True
        rodadas_tendencia = 0
        numeros_tendencia = [n for n in range(1,37)
                             if n%2==1 and n in vermelhos and n in baixos]
        bot.send_message(GRUPO_ID,
f"""🔥 FILTRO INTELIGENTE ATIVADO

Entrar nos números: {sorted(numeros_tendencia)}
(Válido por 3 rodadas)
""")

# ================= COMANDOS =================
@bot.message_handler(commands=['start'])
def start(msg):
    global aguardando_banca
    if msg.from_user.id != ADMIN_ID:
        return
    aguardando_banca = True
    bot.send_message(msg.chat.id,"Digite o valor da banca:")

@bot.message_handler(func=lambda m: m.from_user.id == ADMIN_ID and m.text.replace('.','',1).isdigit())
def salvar_banca(msg):
    global banca, aguardando_banca, painel_id
    if aguardando_banca:
        banca = float(msg.text)
        aguardando_banca = False
        painel = bot.send_message(GRUPO_ID,painel_texto(),reply_markup=teclado())
        painel_id = painel.message_id

# ================= CLIQUE =================
@bot.callback_query_handler(func=lambda call: True)
def clique(call):
    global numeros

    if call.from_user.id != ADMIN_ID:
        return

    num = int(call.data)
    numeros.append(num)
    atualizar_placar(num)

    bot.edit_message_text(
        painel_texto(),
        GRUPO_ID,
        painel_id,
        reply_markup=teclado()
    )

    verificar_estrategias(num)
    analisar_tendencia(num)

    if len(numeros) == 15:
        bot.send_message(GRUPO_ID,
f"""📊 RESUMO 15 RODADAS

Par {placar['par']} x {placar['impar']} Ímpar
Preto {placar['preto']} x {placar['vermelho']} Vermelho
Alto {placar['alto']} x {placar['baixo']} Baixo
""")
        resetar()

print("🔥 SNIPER VIP ULTRA PROFISSIONAL ONLINE 🔥")
bot.infinity_polling()
