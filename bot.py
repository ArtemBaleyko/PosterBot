import telebot
import config
import sqlite3

from datetime import time
from telebot import types

is_manager = False
is_worker = False
is_valid_user = False
new_user = False
username = ''
user_role = ''
task_user = " "
task_descriprion = " "
task_name = " "
task_time = " "
mas_tasks = ["Уборка кухни", "Уборка столов", "Закрытие ресторана"]
tasks_list = "\n"
t_chat_id = 633616258

bot = telebot.TeleBot(config.TOKEN)


@bot.message_handler(commands = ['start'])
def privit(message):
    print(message.from_user.username + " connected")
    with sqlite3.connect("bot_database.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""SELECT username FROM members WHERE role='admin'""")
        admins = cursor.fetchall()
        for row in admins:
            if message.from_user.username in row:
                global is_manager
                is_manager = True
                print(message.from_user.username + " connected as admin")
                cursor.execute("""UPDATE members SET chat_id=? WHERE username=?""",[message.chat.id, message.from_user.username])
                conn.commit()
                break
        
        cursor.execute("""SELECT username FROM members WHERE role='worker'""")
        workers = cursor.fetchall()
        for row in workers:
            if message.from_user.username in row:
                global is_worker
                is_worker = True
                print(message.from_user.username + " connected as worker")
                cursor.execute("""SELECT chat_id FROM members WHERE username=?""", [message.from_user.username])
                result = cursor.fetchall()
                if result[0][0] is None:
                    global new_user
                    new_user = True
                    cursor.execute("""UPDATE members SET chat_id=? WHERE username=?""",[message.chat.id, message.from_user.username])
                    print(row)
                    conn.commit()
                else:
                    new_user = False
                break

        keyboard = types.InlineKeyboardMarkup(row_width=1)
        button1 = types.InlineKeyboardButton("Начать день!", callback_data="bstart")
        keyboard.add(button1)
        global username
        username = message.from_user.username
        if is_worker == True and new_user == True:
            bot.send_message(message.chat.id, '💬\n\nВас преветсвует *Имя_Бота* Bot👋👋\nДавайте начнем рабочий день?\n\n💬', reply_markup=keyboard)
        elif is_manager == True:
            bot.send_message(message.chat.id, '💬\n\nИ снова здравствуйте!👋👋\n\nДавайте начнем рабочий день?\n\n💬',reply_markup=keyboard)
        elif is_worker == True:
            bot.send_message(message.chat.id, '💬\n\nИ снова здравствуйте!👋👋\n\nДавайте начнем рабочий день?\n\n💬', reply_markup=keyboard)
        else:
            bot.send_message(message.chat.id, '💬\n\nК сожалению вы не явлеетесь сотрудником😭\n\nЕсли возникла ошибка, обратитесь к своему менеджеру!\n\n💬')

@bot.callback_query_handler(func =lambda call: True)
def user_login(call):
    if is_worker is True:
        bot.send_message(call.message.chat.id, '💬\n\nВы успешно вошли как ' + username + '😉\n\n💬')
        bot.send_message(call.message.chat.id, 'Выберите одну из активных задач: \n\n👇👇👇👇👇👇👇👇')
    elif is_manager is True:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button1 = types.KeyboardButton("История задач")
        button2 = types.KeyboardButton("Создать задачу")
        button3 = types.KeyboardButton("Добавить сотрудника") 
        keyboard.add(button1,button2,button3) 
        bot.send_message(call.message.chat.id, '💬\n\nВы успешно вошли как ' + username + '😉\n\n💬')
        bot.send_message(call.message.chat.id, '⚡️Как менеджер вы можете:\n\n   1.Узнать список задач 📋\n\n   2.Создать новую задачу 📝\n\n   3.Добавить сотрудника 👨‍💻\n\n👇👇👇👇👇👇👇👇', reply_markup=keyboard)

@bot.message_handler(content_types=['text'])
def manager_readkey(message,):
    try:
        if message.text == "История задач":
            bot.send_message(message.chat.id, 'Вы выбрали Историю задач')
        elif message.text == "Создать задачу":
            bot.send_message(message.chat.id, 'Вы выбрали Создать задачу')     
            msg = bot.send_message(message.chat.id, "Введите имя сотрудника: ")              #msg формирует сообщение для перехода в след функц
            bot.register_next_step_handler(msg, choose_name_for_worker)     #переход в след функцию (message_string, method_name) желательно юзать try - эта штука может крашиться
        elif message.text == "Добавить сотрудника":
            bot.send_message(message.chat.id, 'Вы выбрали Добавить сотрудника')
            msg = bot.send_message(message.chat.id, "Введите имя сотрудника: ")
            bot.register_next_step_handler(msg, add_new_user_name)   
    except:
        bot.send_message(message.chat.id, "Something go wrong")
 
def choose_name_for_worker(message):
 try:
     global username
     username = message.text.replace('@','')
     msg = bot.reply_to(message, "Название задачи: ")
     bot.register_next_step_handler(msg, manager_add_task_name)
 except:
     bot.send_message(message.chat.id, "choose_name_for_worker")

def manager_add_task_name(message):
    try:
        global task_name
        task_name = message.text
        msg = bot.reply_to(message, "Примечание: ") 
        bot.register_next_step_handler(msg, manager_add_task_description)
    except:
        bot.send_message(message.chat.id, "m_add_task_name")
 
def manager_add_task_description(message):
    try:
        global task_descriprion
        task_descriprion = message.text
        msg = bot.reply_to(message, "Время (ЧЧ:ММ): ") 
        bot.register_next_step_handler(msg, manager_add_task_time)
    except:
        bot.send_message(message.chat.id, "m_add_task_deskr")
 

def manager_add_task_time(message):
    try:
        global task_time
        task_time = message.text
        keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        keyboard.add('Подтвердить')
        keyboard.one_time_keyboard = True
        keyboard.resize_keyboard = 0.5
        msg = bot.reply_to(message, "Подтвердите задачу..." + '\n\n📋  ' + task_name + '\n\n' + task_descriprion + '\n\n' +'🕑  '+task_time, reply_markup = keyboard)
        bot.register_next_step_handler(msg, manager_send_task)
    except:
        bot.send_message(message.chat.id, "m_add_task_time")
 

def manager_send_task(message):
    with sqlite3.connect("bot_database.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""SELECT id, chat_id FROM members WHERE username=?""",[username])
        user = cursor.fetchall()
        bot.send_message(user[0][1], '‼️  У вас новая задача  ‼️')
        bot.send_message(user[0][1], '📋  ' + task_name + '\n\n' + task_descriprion + '\n\n' +'🕑  '+ task_time)
        cursor.execute("""INSERT INTO check_list (name, description, task_time, member_id) VALUES (?,?,?,?)""",[task_name, task_descriprion, task_time, user[0][0]])
        conn.commit()


def add_new_user_name(message):
    try:
        global username
        username = message.text.replace('@', '')
        msg = bot.reply_to(message, "Его должность: ") 
        bot.register_next_step_handler(msg, add_new_user_role)
    except:
        bot.send_message(message.chat.id, "add_new_user_name")

def add_new_user_role(message):
    try:
        global user_role
        user_role = message.text
        keyboard1 = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        keyboard1.add('Подтвердить')
        keyboard1.one_time_keyboard = True
     #keyboard1.resize_keyboard = 0.1
        msg = bot.send_message(message.chat.id, "Подтвердите нового пользователя..." + '\n\n👤  ' + username + '\n\n👤  ' + user_role + '\n\n' +'👇👇👇👇👇👇👇👇', reply_markup = keyboard1)
        bot.register_next_step_handler(msg, add_new_user_toBD)
    except:
        bot.send_message(message.chat.id, "add_new_user_role")

def add_new_user_toBD(message):
    with sqlite3.connect("bot_database.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""INSERT INTO members (username, role) VALUES (?,?)""",[username, user_role])
        conn.commit()
        bot.send_message(message.chat.id, 'Сотрудник ' + username + ' успешно добавлен')


# RUN
bot.polling(none_stop=True)