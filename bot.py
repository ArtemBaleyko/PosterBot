import telebot
import config 

bot = telebot.TeleBot(config.TOKEN)

@bot.message_handler(commands = ['start'])
def privit(message):
    bot.send_message(message.chat.id, "Privit")

# RUN
bot.polling(none_stop=True)