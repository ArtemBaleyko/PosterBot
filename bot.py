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
task_description = " "
task_name = " "
task_time = " "
mas_tasks = ["Уборка кухни", "Уборка столов", "Закрытие ресторана"]
tasks_list = "\n"
bmenu = True
workers = []

bot = telebot.TeleBot(config.TOKEN)


@bot.message_handler(commands = ['start'])
def privit(message):
    print(message.from_user.username + " connected")
    with sqlite3.connect(config.DB_NAME) as conn:
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
            bot.send_message(message.chat.id, '💬\n\nВас преветсвует Check List Administrator Bot👋👋\nДавайте начнем рабочий день?\n\n💬', reply_markup=keyboard)
        elif is_manager == True:
            bot.send_message(message.chat.id, '💬\n\nИ снова здравствуйте!👋👋\n\nДавайте начнем рабочий день?\n\n💬',reply_markup=keyboard)
        elif is_worker == True:
            bot.send_message(message.chat.id, '💬\n\nИ снова здравствуйте!👋👋\n\nДавайте начнем рабочий день?\n\n💬', reply_markup=keyboard)
        else:
            bot.send_message(message.chat.id, '💬\n\nК сожалению вы не явлеетесь сотрудником😭\n\nЕсли возникла ошибка, обратитесь к своему менеджеру!\n\n💬')

@bot.callback_query_handler(lambda call: call.data =="bstart")
def user_login(call):
    global bmenu
    if  bmenu is True:
        bot.send_message(call.message.chat.id, '💬\n\nВы успешно вошли как ' + username + ' 😉\n\n💬')
        bmenu = False
    if is_worker is True:
        with sqlite3.connect(config.DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("""SELECT id FROM members WHERE username=?""",[username])
            user = cursor.fetchall()
            user_id = user[0][0]
            cursor.execute("""SELECT name, description, task_time, id FROM check_list WHERE member_id=?""",[user_id])
            result = cursor.fetchall()
            print(result)
            bot.send_message(call.message.chat.id, '🌐     Вы в главном меню\n\nНажмите "Показать список активных задачи" и выберите какую задачу вы хотите завершить.\n\n👇👇👇👇👇👇👇👇')
            for row in result: 
                task_name = row[0]
                task_description = row[1]
                task_time = row[2]
                task_id = row[3]
                keyboard = types.InlineKeyboardMarkup(row_width=1)
                button1 = types.InlineKeyboardButton("Выполнено", callback_data="complete_task")
                keyboard.add(button1)
                bot.send_message(call.message.chat.id, '‼️  У вас новая задача  ‼️')
                bot.send_message(call.message.chat.id, '#' + str(task_id) + ' '+ '\n📋  ' + task_name + '\n\n' + task_description + '\n\n' +'🕑  '+ task_time,reply_markup=keyboard)
        
    elif is_manager is True:
        keyboard = types.ReplyKeyboardMarkup()
        button1 = types.KeyboardButton("История задач 📋")
        button2 = types.KeyboardButton("Создать задачу 📝")
        button3 = types.KeyboardButton("Добавить сотрудника 👨‍💻")
        button4 = types.KeyboardButton("Удалить сотрудника ❌")
        keyboard.resize_keyboard=True
        keyboard.one_time_keyboard = True
        keyboard.add(button1,button2,button3, button4) 
        bot.send_message(call.message.chat.id, '🌐     Вы в главном меню\n\n⚡️Как менеджер вы можете:\n\n   1.История всех задач 📋\n\n   2.Создать новую задачу 📝\n\n   3.Добавить сотрудника 👨‍💻\n\n   4.Удалить сотрудника ❌\n\n👇👇👇👇👇👇👇👇', reply_markup=keyboard)


@bot.callback_query_handler(lambda call: call.data =="complete_task")
def task_complete(call):
    with sqlite3.connect(config.DB_NAME) as conn:
        cursor = conn.cursor()
        message = call.message.text.split(" ")
        task_id = int(message[0].replace('#', ''))
        bot.delete_message(call.message.chat.id, call.message.message_id)
        cursor.execute("""SELECT name FROM check_list WHERE id=?""",[task_id])
        task_name = cursor.fetchall()[0][0]
        cursor.execute("""DELETE FROM check_list WHERE id=?""",[task_id])
        conn.commit()
        cursor.execute("""SELECT chat_id FROM members WHERE role='admin'""")
        admins = cursor.fetchall()
        for row in admins:
            bot.send_message(row[0],"Задача #{0} {1} выполнена ✅".format(task_id, task_name))
    

@bot.message_handler(content_types=['text'])
def manager_readkey(message,):
    try:
        khide = telebot.types.ReplyKeyboardRemove()
        if message.text == "История задач 📋":
            bot.send_message(message.chat.id, '📋  Вы выбрали ИСТОРИЯ ЗАДАЧ  📋\n\nСписок задач\n👇👇👇👇👇👇👇👇', reply_markup = khide)
            with sqlite3.connect(config.DB_NAME) as conn:
                cursor = conn.cursor()
                cursor.execute("""SELECT c.id, c.name, c.description, c.task_time, m.username FROM check_list c LEFT JOIN
                                    members m WHERE c.member_id=m.id """)
                tasks = cursor.fetchall()
                for row in tasks:
                    task_id = row[0]
                    task_name = row[1]
                    task_description = row[2]
                    task_time = row[3]
                    task_owner = row[4]
                    bot.send_message(message.chat.id, '#' + str(task_id) +' '+'\n📋  ' + task_name + '\n\n' + task_description + '\n\n' +'🕑  '+ task_time + '\n\n' + 'Ответственный: ' + task_owner)
            keyboard = types.InlineKeyboardMarkup(row_width=1)
            button1 = types.InlineKeyboardButton("Назад в меню 📲", callback_data="bstart")
            keyboard.add(button1)
            bot.send_message(message.chat.id, "Назад в меню", reply_markup = keyboard)
        elif message.text == "Создать задачу 📝":
            bot.send_message(message.chat.id, '📝  Вы выбрали СОЗДАТЬ ЗАДАЧУ  📝\n\n',reply_markup = khide)
            with sqlite3.connect(config.DB_NAME) as conn:
                cursor = conn.cursor()
                cursor.execute("""SELECT username FROM members WHERE NOT role='admin'""")
                worker = cursor.fetchall()
                strl = "📜Список действующих сотрудников:\n\n"
                for row in worker:
                    strl += row[0]
                    strl += '\n'
                strl += "\nВведите имя сотрудника\n  👇👇👇👇👇👇👇👇"     
            msg = bot.send_message(message.chat.id, strl)              
            bot.register_next_step_handler(msg, choose_name_for_worker)     
        elif message.text == "Добавить сотрудника 👨‍💻":
            bot.send_message(message.chat.id, '👨‍💻  Вы выбрали ДОБАВИТЬ СОТРУДНИКА  👨‍💻',reply_markup = khide)
            msg = bot.send_message(message.chat.id, "✏️  Введите имя сотрудника: ")
            bot.register_next_step_handler(msg, add_new_user_name)
        elif message.text == "Удалить сотрудника ❌":
            bot.send_message(message.chat.id, '❌  Вы выбрали Удалить сотрудника  ❌',reply_markup = khide)  
            #список сотрудников из бд в виде строки
            with sqlite3.connect(config.DB_NAME) as conn:
                cursor = conn.cursor()
                cursor.execute("""SELECT username FROM members WHERE NOT role='admin'""")
                global workers
                workers = cursor.fetchall()
                strl = "📜Список действующих сотрудников:\n\n"
                for row in workers:
                    strl += row[0]
                    strl += '\n'
                strl += "\nВведите имя сотрудника для удаления\n  👇👇👇👇👇👇👇👇"
            #strl = "📜Список действующих сотрудников:\n\nсотрудник_1\nсотрудник_2\nсотрудник_3\nсотрудник_4\nсотрудник_5\nсотрудник_6\n\nВведите имя сотрудника для удаления\n  👇👇👇👇👇👇👇👇"
            msg = bot.send_message(message.chat.id, strl)
            bot.register_next_step_handler(msg, delete_user_by_name)   
    except:
        bot.send_message(message.chat.id, "😱 Упс, что-то пошло не так(\n\n       Попробуйте позже!")
 
def delete_user_by_name(message):
    user_to_delete = message.text.replace('@','')
    #проверка на валидность
    #удаление из бд
    #user_chat_id =
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    button1 = types.InlineKeyboardButton("Назад в меню 📲", callback_data="bstart")
    keyboard.add(button1)
    if user_is_worker(user_to_delete) is True:
        with sqlite3.connect(config.DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("""SELECT chat_id, id FROM members WHERE username=?""",[user_to_delete])
            chat_id = cursor.fetchall()[0][0]
            user_id = cursor.fetchall()[0][1]
            cursor.execute("""DELETE FROM check_list WHERE member_id=?"""[user_id])
            cursor.execute("""DELETE FROM members WHERE username=?""",[user_to_delete])
            conn.commit()
            bot.send_message(message.chat.id, "❌ Сотрудник " + user_to_delete + " успешно удален! ❌",reply_markup=keyboard)
            bot.send_message(chat_id, "Менеджер " + message.from_user.username+ " убрал вас и белого списка\nНам жаль с вами расставаться😢\n") 
    else:
        bot.send_message(message.chat.id, "Такого сотрудника не существует", reply_markup=keyboard)

def choose_name_for_worker(message):
    try:
        global username
        username = message.text.replace('@','')
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        button1 = types.InlineKeyboardButton("Назад в меню 📲", callback_data="bstart")
        keyboard.add(button1)
        if user_is_worker(username):
            msg = bot.reply_to(message, "✏️  Название задачи: ")
            bot.register_next_step_handler(msg, manager_add_task_name)
        else:
            bot.send_message(message.chat.id, "🔎 Такого сотрудника не существует", reply_markup=keyboard)
    except:
        bot.send_message(message.chat.id, "😱 Упс, что-то пошло не так(\n\n       Попробуйте позже!")

def manager_add_task_name(message):
    try:
        global task_name
        task_name = message.text
        msg = bot.reply_to(message, "✏️  Примечание к задачи: ") 
        bot.register_next_step_handler(msg, manager_add_task_description)
    except:
        bot.send_message(message.chat.id,"😱 Упс, что-то пошло не так(\n\n       Попробуйте позже!")
 
def manager_add_task_description(message):
    try:
        global task_description
        task_description = message.text
        msg = bot.reply_to(message, "🕐  Время: \n\n⭐️подсказка - строго ЧЧ:ММ⭐️")
        bot.register_next_step_handler(msg, manager_add_task_time)
    except:
        bot.send_message(message.chat.id, "😱 Упс, что-то пошло не так(\n\n       Попробуйте позже!")
 

def manager_add_task_time(message):
    try:
        global task_time
        task_time = message.text
        if time_is_valid(task_time) is True:
            keyboard = types.ReplyKeyboardMarkup()
            keyboard.add('Подтвердить и Отправить📌')
            keyboard.one_time_keyboard = True
            keyboard.resize_keyboard = True
            msg = bot.send_message(message.chat.id, "✅Подтвердите задачу..." + '\n\n📋  ' + task_name + '\n\n' + task_description + '\n\n' +'🕑  '+task_time, reply_markup = keyboard)
            bot.register_next_step_handler(msg, manager_send_task)
            keyboard = types.ReplyKeyboardMarkup()
        else:
            msg = bot.reply_to(message, "💢Ошибка ввода \n\n⭐️подсказка - строго ЧЧ:ММ⭐️")
            bot.register_next_step_handler(msg, manager_add_task_time)
    except:
        bot.send_message(message.chat.id,"😱 Упс, что-то пошло не так(\n\n       Попробуйте позже!")
 

def manager_send_task(message):
    with sqlite3.connect(config.DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""SELECT id, chat_id FROM members WHERE username=?""",[username])
        user = cursor.fetchall()
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        button1 = types.InlineKeyboardButton("Назад в меню 📲", callback_data="bstart")
        keyboard.add(button1)
        bot.send_message(message.chat.id, "Готово!  🎉\n\n👇 Вернуться в меню 👇", reply_markup = keyboard)
        bot.send_message(user[0][1], '‼️  У вас новая задача  ‼️')
        bot.send_message(user[0][1], '📋  ' + task_name + '\n\n' + task_description + '\n\n' +'🕑  '+ task_time)
        cursor.execute("""INSERT INTO check_list (name, description, task_time, member_id) VALUES (?,?,?,?)""",[task_name, task_description, task_time, user[0][0]])
        conn.commit()


def add_new_user_name(message):
    try:
        global username
        username = message.text.replace('@', '')
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        button1 = types.InlineKeyboardButton("Назад в меню 📲", callback_data="bstart")
        keyboard.add(button1)
        if user_exist(username) is not True:
            msg = bot.reply_to(message, "👩‍✈️👨‍✈️  Его должность: ") 
            bot.register_next_step_handler(msg, add_new_user_role)
        else:
            bot.send_message(message.chat.id, "Такой сотрудник уже существует", reply_markup=keyboard)
    except:
        bot.send_message(message.chat.id, "😱 Упс, что-то пошло не так(\n\n       Попробуйте позже!")

def add_new_user_role(message):
    try:
        global user_role
        user_role = message.text
        keyboard = types.ReplyKeyboardMarkup()
        keyboard.add('Подтвердить📌')
        keyboard.one_time_keyboard = True
        keyboard.resize_keyboard = True
        msg = bot.send_message(message.chat.id, "✅Подтвердите нового пользователя..." + '\n\n👤  ' + username + '\n\n👤  ' + user_role + '\n\n' +'👇👇👇👇👇👇👇👇', reply_markup = keyboard)
        bot.register_next_step_handler(msg, add_new_user_toBD)
    except:
        bot.send_message(message.chat.id, "😱 Упс, что-то пошло не так(\n\n       Попробуйте позже!")

def add_new_user_toBD(message):
    with sqlite3.connect(config.DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""INSERT INTO members (username, role) VALUES (?,?)""",[username, user_role])
        conn.commit()
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        button1 = types.InlineKeyboardButton("Назад в меню 📲", callback_data="bstart")
        keyboard.add(button1)
        bot.send_message(message.chat.id, 'Сотрудник ' + username + ' успешно добавлен  🎉\n\n👇 Вернуться в меню 👇', reply_markup=keyboard)


def time_is_valid(task_time):
    str_time = task_time.replace(':',' ').split(' ')
    try:
        hour = int(str_time[0])
        minute = int(str_time[1])
        if hour<=23 and hour >=0 and minute>=0 and minute <=60:
            return True
        else:
            return False
    except(ValueError):
        return False
    
def user_is_worker(username):
    with sqlite3.connect(config.DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""SELECT username FROM members WHERE NOT role='admin'""")
        workers = cursor.fetchall()
        for row in workers:
            if username in row:
                return True
        return False

def user_exist(username):
    with sqlite3.connect(config.DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""SELECT username FROM members""")
        workers = cursor.fetchall()
        for row in workers:
            if username in row:
                return True
        return False
# RUN
bot.polling(none_stop=True)