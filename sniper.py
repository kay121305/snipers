import telebot
import os

TOKEN = os.getenv("TOKEN")
bot = telebot.TeleBot(TOKEN)

GRUPO_ID = -1003629208122
ADMIN_ID = 8431121309

# ================= NUMEROS =================

vermelhos = {1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36}
pretos = {2,4,6,8,10,11,13,15,17,20,22,24,26,28,29,31,33,35}

altos = set(range(19,37))
baixos = set(range(1,19))

grupo_A = {3,6,9}
grupo_B = {0,10}

# ================= CONTROLE =================

numeros = []
placar = {}
banca = {}
entrada_ativa = None
alerta_enviado = False
tentativas = 0

# ================= FUNÇÕES =================

def resetar_placar():
    global placar
    placar = {
        "par":0,"impar":0,
        "preto":0,"vermelho":0,
        "alto":0,"baixo":0
    }

resetar_placar()

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

def mostrar_placar():
    return f"""
📊 PLACAR AO VIVO ({len(numeros)}/15)

Par: {placar['par']} | Ímpar: {placar['impar']}
Preto: {placar['preto']} | Vermelho: {placar['vermelho']}
Alto: {placar['alto']} | Baixo: {placar['baixo']}
"""

def enviar_resumo_15():
    bot.send_message(GRUPO_ID, f"""
📈 RESULTADO DAS 15 RODADAS

Par {placar['par']} x {placar['impar']} Ímpar
Preto {placar['preto']} x {placar['vermelho']} Vermelho
Alto {placar['alto']} x {placar['baixo']} Baixo
""")

def analisar_tendencia():
    total = len(numeros)
    if total < 12:
        return

    for chave in ["par","impar","preto","vermelho","alto","baixo"]:
        if placar[chave] >= 8:
            if chave == "par":
                tendencia = "ÍMPAR"
                nums = [n for n in range(37) if n % 2 == 1]
            elif chave == "impar":
                tendencia = "PAR"
                nums = [n for n in range(37) if n % 2 == 0]
            elif chave == "preto":
                tendencia = "VERMELHO"
                nums = list(vermelhos)
            elif chave == "vermelho":
                tendencia = "PRETO"
                nums = list(pretos)
            elif chave == "alto":
                tendencia = "BAIXO"
                nums = list(baixos)
            elif chave == "baixo":
                tendencia = "ALTO"
                nums = list(altos)

            bot.send_message(GRUPO_ID,
                f"⚠ {chave.upper()} dominando!\n"
                f"🎯 Entrar em {tendencia}\n"
                f"Números: {sorted(nums)}"
            )
            break

def enviar_gestor(qtd_numeros):
    if ADMIN_ID not in banca:
        return

    saldo = banca[ADMIN_ID]

    base = saldo * 0.24
    medio = saldo * 0.48
    alto = saldo * 1.0

    def calcular(valor_total):
        ficha = round(valor_total / qtd_numeros,2)
        ganho = ficha * 36
        lucro = round(ganho - valor_total,2)
        return ficha, ganho, lucro

    f1,g1,l1 = calcular(base)
    f2,g2,l2 = calcular(medio)
    f3,g3,l3 = calcular(alto)

    bot.send_message(GRUPO_ID, f"""
💰 GESTÃO DE BANCA

🔹 Conservador
Ficha: R${f1}
Ganho: R${g1}
Lucro: R${l1}

🔹 Médio
Ficha: R${f2}
Ganho: R${g2}
Lucro: R${l2}

🔹 Agressivo
Ficha: R${f3}
Ganho: R${g3}
Lucro: R${l3}
""")

def verificar_estrategia(num):
    global entrada_ativa, alerta_enviado, tentativas

    if entrada_ativa == "A":
        if num in grupo_A:
            bot.send_message(GRUPO_ID,"✅ GREEN ESTRATÉGIA A")
            entrada_ativa = None
            alerta_enviado = False
            return

    if entrada_ativa == "B":
        if num in grupo_B:
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
            return

        if not any(n in grupo_B for n in ultimos10):
            entrada_ativa = "B"
            alerta_enviado = True
            bot.send_message(GRUPO_ID,
                f"🚨 ENTRAR AGORA\n\nApós o número: {num}\n\n🎯 Estratégia B\nEntrar: 0 - 10")
            enviar_gestor(2)
            return

# ================= COMANDOS =================

@bot.message_handler(commands=['start'])
def start(msg):
    if msg.from_user.id != ADMIN_ID:
        bot.send_message(msg.chat.id,"🔒 Apenas admin.")
        return
    bot.send_message(msg.chat.id,"Digite o saldo da banca:")

@bot.message_handler(func=lambda m: m.from_user.id == ADMIN_ID and m.text.isdigit())
def salvar_banca(msg):
    banca[ADMIN_ID] = float(msg.text)
    bot.send_message(msg.chat.id,f"💰 Banca registrada: R${msg.text}")

@bot.message_handler(func=lambda m: m.from_user.id == ADMIN_ID and m.text.isdigit())
def receber_numero(msg):
    global numeros
    num = int(msg.text)

    if num < 0 or num > 36:
        return

    numeros.append(num)
    atualizar_placar(num)

    bot.send_message(GRUPO_ID, mostrar_placar())

    verificar_estrategia(num)
    analisar_tendencia()

    if len(numeros) == 15:
        enviar_resumo_15()
        numeros.clear()
        resetar_placar()

print("🔥 SNIPER VIP COMPLETO ONLINE 🔥")
bot.infinity_polling()
