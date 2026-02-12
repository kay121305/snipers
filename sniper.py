import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import os

# ================= CONFIGURAÇÃO =================
TOKEN = os.getenv("TOKEN")
bot = telebot.TeleBot(TOKEN)

GRUPO_ID = -1003629208122  # ID do grupo VIP
ADMIN_ID = 8431121309       # Seu ID

# ================= DEFINIÇÃO DE CORES E GRUPOS =================
vermelhos = {1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36}
pretos = {2,4,6,8,10,11,13,15,17,20,22,24,26,28,29,31,33,35}
altos = set(range(19,37))
baixos = set(range(1,19))

# Estratégias
grupo_A = {3,6,9,13,16,19,23,26,29,33,36}  # DG du GRAKRAL
grupo_B = {19,15,32,0,26,3,35,12,28,8,23,10,5}  # Makako LK

# ================= VARIÁVEIS GLOBAIS =================
numeros = []
placar = {"par":0,"impar":0,"preto":0,"vermelho":0,"alto":0,"baixo":0}
painel_id = None
mensagens_reset = []

entrada_ativa = None
grupo_entrada = None
gales = 0
numero_alerta = None
nome_jogada = ""

filtro_ativo = False
numeros_filtro = []
gales_filtro = 0

banca = 0
aguardando_banca = False

# ================= FUNÇÕES =================
def resetar():
    """Reseta contadores e variáveis de rodadas"""
    global numeros, placar, entrada_ativa, gales, numero_alerta
    global filtro_ativo, numeros_filtro, gales_filtro, grupo_entrada, nome_jogada

    numeros.clear()
    placar.update({"par":0,"impar":0,"preto":0,"vermelho":0,"alto":0,"baixo":0})
    entrada_ativa = None
    gales = 0
    numero_alerta = None
    grupo_entrada = None
    nome_jogada = ""
    filtro_ativo = False
    numeros_filtro.clear()
    gales_filtro = 0

def limpar_mensagens():
    """Apaga mensagens antigas do painel"""
    global mensagens_reset
    for msg_id in mensagens_reset:
        try:
            bot.delete_message(GRUPO_ID, msg_id)
        except:
            continue
    mensagens_reset.clear()

# ================= TECLADO 0–36 =================
def teclado():
    """Gera teclado interativo 0–36"""
    kb = InlineKeyboardMarkup(row_width=6)
    botoes = []
    for i in range(37):
        cor = ""
        if i in pretos:
            cor = "⚫"
        elif i in vermelhos:
            cor = "🔴"
        botoes.append(InlineKeyboardButton(f"{i}{cor}", callback_data=str(i)))
    kb.add(*botoes)
    return kb

# ================= PAINEL =================
def painel_texto():
    """Texto do painel atualizado"""
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

# ================= GESTOR DE BANCA =================
def enviar_gestor(numeros_aposta):
    """Envia sugestões de apostas com base na banca"""
    global mensagens_reset
    if banca <= 0:
        return

    conservador = round(banca * 0.02,2)
    medio = round(banca * 0.05,2)
    agressivo = round(banca * 0.10,2)

    msg = bot.send_message(GRUPO_ID,
f"""💰 GESTÃO DE BANCA - {nome_jogada}

Entrada: {sorted(numeros_aposta)}

🔹 Conservador: R${conservador} por ficha
🔸 Médio: R${medio} por ficha
🔺 Agressivo: R${agressivo} por ficha
""")
    mensagens_reset.append(msg.message_id)

# ================= ESTRATEGIAS =================
def verificar_sinal_10_rodadas():
    """Checa se Estratégia A ou B deve disparar"""
    global entrada_ativa, grupo_entrada, gales, numero_alerta, nome_jogada
    ultimos10 = numeros[-10:] if len(numeros) >= 10 else numeros

    # Estratégia A
    if not any(n in grupo_A for n in ultimos10):
        entrada_ativa = True
        grupo_entrada = grupo_A
        numero_alerta = ultimos10[-1] if ultimos10 else None
        gales = 0
        nome_jogada = "DG du GRAKRAL"
        msg = bot.send_message(GRUPO_ID,
f"""🚨 SINAL ESTRATÉGIA A - {nome_jogada} (10 rodadas sem vir)

Último número antes do sinal: {numero_alerta}
Entrar nos números: {sorted(grupo_A)}
""")
        mensagens_reset.append(msg.message_id)
        enviar_gestor(grupo_A)

    # Estratégia B
    elif not any(n in grupo_B for n in ultimos10):
        entrada_ativa = True
        grupo_entrada = grupo_B
        numero_alerta = ultimos10[-1] if ultimos10 else None
        gales = 0
        nome_jogada = "Makako LK"
        msg = bot.send_message(GRUPO_ID,
f"""🚨 SINAL ESTRATÉGIA B - {nome_jogada} (10 rodadas sem vir)

Último número antes do sinal: {numero_alerta}
Entrar nos números: {sorted(grupo_B)}
""")
        mensagens_reset.append(msg.message_id)
        enviar_gestor(grupo_B)

# ================= RESUMO 15 RODADAS =================
def resumo_15_rodadas():
    """Envia resumo e filtro inteligente após 15 rodadas"""
    global numeros, placar, filtro_ativo, numeros_filtro, gales_filtro, mensagens_reset

    msg = bot.send_message(GRUPO_ID,
f"""📊 RESUMO 15 RODADAS

Par {placar['par']} x {placar['impar']} Ímpar
Preto {placar['preto']} x {placar['vermelho']} Vermelho
Alto {placar['alto']} x {placar['baixo']} Baixo
""")
    mensagens_reset.append(msg.message_id)

    # Filtro inteligente
    numeros_filtro.clear()
    if placar["par"] > placar["impar"]:
        numeros_filtro += [n for n in range(37) if n%2==1]
    else:
        numeros_filtro += [n for n in range(37) if n%2==0]

    if placar["preto"] > placar["vermelho"]:
        numeros_filtro = [n for n in numeros_filtro if n in vermelhos]
    else:
        numeros_filtro = [n for n in numeros_filtro if n in pretos]

    if placar["alto"] > placar["baixo"]:
        numeros_filtro = [n for n in numeros_filtro if n in baixos]
    else:
        numeros_filtro = [n for n in numeros_filtro if n in altos]

    if numeros_filtro:
        filtro_ativo = True
        gales_filtro = 0
        msg = bot.send_message(GRUPO_ID,
f"""🔮 FILTRO INTELIGENTE 15 RODADAS

Números sugeridos (contrário ao que venceu):
{sorted(numeros_filtro)}
Até 3 Gales
""")
        mensagens_reset.append(msg.message_id)

    resetar()

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

@bot.message_handler(commands=['reset'])
def reset(msg):
    if msg.from_user.id != ADMIN_ID:
        return
    limpar_mensagens()
    resetar()
    bot.send_message(GRUPO_ID,"✅ Painel e contadores resetados!")

# ================= CLIQUE =================
@bot.callback_query_handler(func=lambda call: True)
def clique(call):
    global numeros, entrada_ativa, gales, filtro_ativo, gales_filtro

    if call.from_user.id != ADMIN_ID:
        return

    num = int(call.data)
    numeros.append(num)
    atualizar_placar(num)

    # Atualiza painel
    bot.edit_message_text(
        painel_texto(),
        GRUPO_ID,
        painel_id,
        reply_markup=teclado()
    )

    # ================= GREEN Estratégia A/B =================
    if entrada_ativa:
        if num in grupo_entrada:
            bot.send_message(GRUPO_ID,f"✅ GREEN {nome_jogada} no número {num}")
            entrada_ativa = False
            gales = 0
        else:
            gales += 1
            if gales >= 3:
                bot.send_message(GRUPO_ID,f"❌ LOSS {nome_jogada}")
                entrada_ativa = False
                gales = 0

    # ================= GREEN Filtro Inteligente =================
    if filtro_ativo:
        if num in numeros_filtro:
            bot.send_message(GRUPO_ID,f"✅ GREEN FILTRO INTELIGENTE no número {num}")
            filtro_ativo = False
            gales_filtro = 0
        else:
            gales_filtro += 1
            if gales_filtro >= 3:
                bot.send_message(GRUPO_ID,"❌ LOSS FILTRO INTELIGENTE")
                filtro_ativo = False
                gales_filtro = 0

    # Checa sinal de Estratégia A/B após 10 rodadas
    if len(numeros) >= 10:
        verificar_sinal_10_rodadas()

    # Resumo após 15 rodadas
    if len(numeros) == 15:
        resumo_15_rodadas()

# ================= INICIO =================
print("🔥 SNIPER VIP PAINEL 0–36 INTERATIVO COMPLETO 🔥")
bot.infinity_polling()
