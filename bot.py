import telebot
import config
import sqlite3 

from telebot import types

conn = sqlite3.connect("bot_database.db")
cursor = conn.cursor()

bot = telebot.TeleBot(config.TOKEN)

@bot.message_handler(commands = ['start'])
def privit(message):
    bot.send_message(message.chat.id, "Privit")

# RUN
bot.polling(none_stop=True)