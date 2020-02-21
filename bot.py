import telebot
import config
import sqlite3 

from telebot import types

is_manager = False
is_worker = False

bot = telebot.TeleBot(config.TOKEN)

is_valid_user = False

@bot.message_handler(commands = ['start'])
def privit(message):
    with sqlite3.connect("bot_database.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""SELECT username FROM members WHERE role='admin'""")
        admins = cursor.fetchall()
        for row in admins:
            if message.from_user.username in row:
                global is_manager
                is_manager = True
                cursor.execute("""UPDATE members SET chat_id=? WHERE username=?""",[message.chat.id, message.from_user.username])
                conn.commit()
                break
        
        cursor.execute("""SELECT username FROM members WHERE role='worker'""")
        workers = cursor.fetchall()
        for row in workers:
            if message.from_user.username in row:
                global is_worker
                is_worker = True
                cursor.execute("""UPDATE members SET chat_id=? WHERE username=?""",[message.chat.id, message.from_user.username])
                conn.commit()
                break
        
        if is_worker == True:
            bot.send_message(message.chat.id, 'С возвращением, гнида')
        elif is_manager == True:
            bot.send_message(message.chat.id, 'С возвращением, милорд')
        else:
            bot.send_message(message.chat.id, 'У вас нет доступа к боту')



# RUN
bot.polling(none_stop=True)