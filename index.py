import telebot
import sqlite3
from telebot import types
import time



bot = telebot.TeleBot('') #Токен бота 
global inits
inits = 0
global indexuser
global idUser
indexuser = []
admin = [''] #Юзы админов для управление бота
answernum = 0

def points(user_id):
    try:
        conn = sqlite3.connect('users.db')
        cur = conn.cursor()
        cur.execute('UPDATE users SET points = points + 1 WHERE iduser = ?', (user_id,))
        conn.commit()
        cur.execute('SELECT * FROM users')
        ans = cur.fetchall()
        
                
        print('Hi ', ans, user_id)
    except sqlite3.Error as e:
        print(f"Errors: {e}")
    finally:
        cur.close()
        conn.close()

@bot.message_handler(commands=['start'])
def start(message):
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()

    cur.execute('CREATE TABLE IF NOT EXISTS users (id integer primary key autoincrement, iduser int, name varchar, points integer)')   #создаём таблицу

    #Проверяем зарегестрирован ли человек, если нет то регестрируем
    namesUsers = message.from_user.username
    cur.execute('SELECT * FROM users')
    tabelUserInfo = ''
    nameUsers = cur.fetchall()
    for names in nameUsers:
        tabelUserInfo += f'{names[2]} '
    print(nameUsers)
    if namesUsers is not None and namesUsers in tabelUserInfo:
        print('Человек уже есть в таблице')

    else:
        idUser = message.from_user.id
        cur.execute("INSERT INTO users (name, iduser) VALUES('%s', '%s')" % (namesUsers, idUser))
        print(tabelUserInfo)
        print('Добовляю...')
    conn.commit()
    cur.close()
    conn.close()

    bot.send_message(message.chat.id, text='Привет этот бот создан для викторины в институт ..., дождитесь запуска данной викторины.')
    print(namesUsers)

#команда для просмотра зерегестрированых пользователей



@bot.message_handler(commands=['setings', 'panel'])
def adminpanel(message):
    block = types.InlineKeyboardMarkup()
    nextAnswer = types.InlineKeyboardButton(text='Следущая задача', callback_data='nextansw')
    userInfo = types.InlineKeyboardButton(text='Список пользователей', callback_data='userlist')
    block.add(nextAnswer, userInfo)
    if message.from_user.username in admin:
        bot.send_message(message.chat.id, text='Приветствую в панеле администрарота \n Выберите нужный пункт снизу', reply_markup=block)



@bot.callback_query_handler(func=lambda call: call.data)
def nextansw(call):
    conn = sqlite3.connect('users.db')
    cur = conn.cursor()
    cur.execute('SELECT answerTrue FROM question')
    answertrue = cur.fetchall()
    idUsersbtn = call.from_user.id
    global answernum
    

    user_id = call.from_user.id 
    if call.data == 'userlist':
        cur.execute('SELECT * FROM users')
        info = ''
        nameUsers = cur.fetchall()
        for names in nameUsers:
            info += f'Изернейм: @{names[2]}, ID: {names[1]}, Поинты: {names[3]} \n'
        print(nameUsers)
        blocks = types.InlineKeyboardMarkup()
        exis = types.InlineKeyboardButton(text='Начать игру', callback_data='nextansw')
        delpoin = types.InlineKeyboardButton(text='Обнулить поинты', callback_data='delitpoints')
        blocks.add(exis, delpoin)
        bot.send_message(call.message.chat.id, info, reply_markup=blocks)
        
    elif call.data == 'delitpoints':
         blocks = types.InlineKeyboardMarkup()
         yes = types.InlineKeyboardButton(text='Назад', callback_data='userlist')
         no = types.InlineKeyboardButton(text='Обнулить поинты', callback_data='delpoin')
         blocks.add(yes, no)
         bot.send_message(call.message.chat.id, text='Вы уверены что хотите обнулить прогрес ВСЕХ ПОЛЬЗОВАТЕЛЕЙ?', reply_markup=blocks)
         
    
    elif call.data == 'nextansw':
        
        cur.execute('SELECT iduser FROM users')
        idChat = cur.fetchall()
        
        idChats = ''
        blocks = types.InlineKeyboardMarkup()
        A = types.InlineKeyboardButton(text='А', callback_data='a')
        B = types.InlineKeyboardButton(text='Б', callback_data='b')
        V = types.InlineKeyboardButton(text='В', callback_data='v')
        G = types.InlineKeyboardButton(text='Г', callback_data='g')
        D = types.InlineKeyboardButton(text='Д', callback_data='d')
        blocks.add(A, B, V, G, D)
        for addid in idChat:
            idChats += f'{addid[0]} '
            print(idChats)
            indexuser.append(addid[0])
            idChats == ''
            print(indexuser, idChats)

            
        cur.execute('SELECT question FROM question')
        qestSQL = cur.fetchall()


        inits = 0

        for qestSQLs in qestSQL:  
            cur.execute('SELECT answerOne, answerTwo, answerThree, answerFour, answerFive FROM question')
            answerd = cur.fetchall()
            
            for i in range(len(indexuser)):
                if inits < len(answerd) * len(idChat):
                    # Форматируем ответы с новой строки
                    formatted_answers = '\n'.join(str(answer) for answer in answerd[inits])
                    texts = f'{qestSQLs[0]} \nВарианты ответов:\n{formatted_answers}'
                    bot.send_message(chat_id=indexuser[i], text=texts, reply_markup=blocks)
                    print(inits)

                else:
                    print("Недостаточно ответов для индексации.")
                    break
            inits += 1
            time.sleep(10)
            #если вопросы закончились
            if len(indexuser) < inits:
                 cur.execute('SELECT points FROM users WHERE iduser = ?', (idUsersbtn,))
                 point = cur.fetchall()
                 bot.send_message(call.message.chat.id, text=f'Вопросы закончились! Вы получили {point[0]} поинтов')

            idChats = ''
        




    #Обработчик вопросов
    
    elif call.data == 'a':
            print(answertrue[answernum])
            
            if 'A' in answertrue[answernum]:
                bot.send_message(chat_id=user_id, text='Правильно начислено 1 поинт')
                answernum += 1
                print(idUsersbtn)
                points(idUsersbtn)
                
                
            else:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text='Неправильно')
                answernum += 1
                
    
    elif call.data == 'b':
            print(answertrue[answernum])
            
            if 'B' in answertrue[answernum]:
                bot.send_message(chat_id=user_id, text='Правильно начислено 1 поинт')
                answernum += 1
                print(idUsersbtn)
                points(idUsersbtn)
                
                
            else:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text='Неправильно')
                answernum += 1
                
                
            
    
    elif call.data == 'v':
            print(answertrue[answernum])
            
            if 'V' in answertrue[answernum]:
                bot.send_message(chat_id=user_id, text='Правильно начислено 1 поинт')
                answernum += 1
                print(idUsersbtn)
                points(idUsersbtn)
                
                
            else:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text='Неправильно')
                answernum += 1
                

    elif call.data == 'g':
            print(answertrue[answernum])
            
            if 'G' in answertrue[answernum]:
                bot.send_message(chat_id=user_id, text='Правильно начислено 1 поинт')
                answernum += 1
                print(idUsersbtn)
                points(idUsersbtn)
                
                
            else:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text='Неправильно')
                answernum += 1

    elif call.data == 'd':
            print(answertrue[answernum])
            
            if 'D' in answertrue[answernum]:
                bot.send_message(chat_id=user_id, text='Правильно начислено 1 поинт')
                answernum += 1
                print(idUsersbtn)
                points(idUsersbtn)
                
                
            else:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text='Неправильно')
                answernum += 1
    

bot.infinity_polling()