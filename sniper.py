import telebot
import os

TOKEN = os.getenv("TOKEN")
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, f"SEU ID É: {message.from_user.id}")

print("BOT INICIADO")
bot.infinity_polling()
