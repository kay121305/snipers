import telebot
import os

TOKEN = os.getenv("TOKEN")
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(msg):
    bot.send_message(msg.chat.id, f"ID DO CHAT: {msg.chat.id}")

print("BOT ONLINE")
bot.infinity_polling()
