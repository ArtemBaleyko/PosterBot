import telebot
import config 

from telebot import types

bot = telebot.TeleBot(config.TOKEN)

@bot.message_handler(commands = ['start'])
def privit(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttom1 = types.InlineKeyboardButton("buttom 1", callback_data="1")
    buttom2 = types.InlineKeyboardButton("buttom 2", callback_data="2")
    markup.add(buttom1, buttom2)
    bot.send_message(message.chat.id, "Privit", reply_markup=markup)

# RUN
bot.polling(none_stop=True)