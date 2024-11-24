import telebot
from telebot import types
import config
from database import Database
from search import Search
from send import Send


print("Active")
bot = telebot.TeleBot(config.TOKEN)


@bot.message_handler(commands=["start"])
def start(message):
    database = Database(message.from_user.id)
    # if database.process != 0:
    #     database.save(process=0, name=None, salon=None)
    # bot.send_message(message.chat.id, f'Напишите ваше ФИО')
    #
    # database.save(username=message.from_user.username)
    # print(message)

    database.save(process=1)
    markup = types.InlineKeyboardMarkup()
    for i in ['Гарантии Сертификаты', 'Возвраты', 'Номера']:
        markup.add(types.InlineKeyboardButton(f'Категория: {i}', callback_data=i))
    bot.send_message(message.chat.id, 'Напишите свой запрос или выберите категорию:', reply_markup=markup)



@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    database = Database(call.from_user.id)
    req = call.data

    # Регистрация
    if database.process == 0:
        database.save(salon=req)
        if database.name is not None:
            database.save(process=1)
            database = Database(call.from_user.id)
            bot.send_message(call.message.chat.id, f'Вы {database.name} из {database.salon}')

        bot.edit_message_reply_markup(call.from_user.id, call.message.message_id,
                                     reply_markup=None)

    else:
        if req != 'Ничего не найдено':
            search = Search(None)
            send = Send(search.objects)
            send.get_request(req)
            markup = types.InlineKeyboardMarkup()
            count = 0
            text = ''
            if send.request_type == 1:
                for res in send.send_folder(req):
                    res = res.replace('.txt', '')
                    url = res
                    if res in [i[0] for i in search.get_folders()]:
                        res = f'Категория: {res}'
                    else:
                        res = f'Раздел: {res}'
                    markup.add(types.InlineKeyboardButton(res, callback_data=url))
                    count += 1
                    if count == 10:
                        text += 'Результатов более 10. Показаны первые 10\n\n'
                        break
                text += 'Результат по вашему запросу:'
                bot.edit_message_text(text, call.from_user.id, call.message.message_id, reply_markup=markup)
            elif send.request_type == 2:
                bot.send_message(call.message.chat.id, send.send_file_text(req))
            elif send.request_type == 3:
                bot.send_document(call.message.chat.id, send.send_document(req))
        else:
            bot.send_message(call.message.chat.id, 'Пожалуйста напишите другой запрос')


@bot.message_handler(content_types=["text"])
def handler_text(message):
    database = Database(message.from_user.id)

    if database.process == 0:
        markup = types.InlineKeyboardMarkup()
        for i in database.get_salon():
            if i == '1. Офис':
                i = 'Офис'
            markup.add(types.InlineKeyboardButton(i, callback_data=i))
        bot.send_message(message.chat.id, f'Укажите ваш салон', reply_markup=markup)

    else:
        markup = types.InlineKeyboardMarkup()
        count = 0
        search = Search(message.text)
        text = ''

        for res in search.result:
            res = res.replace('.txt', '')
            url = res
            if res in [i[0] for i in search.get_folders()]:
                res = f'Категория: {res}'
            else:
                res = f'Раздел: {res}'
            markup.add(types.InlineKeyboardButton(res, callback_data=url))
            count += 1
            if count == 10:
                text += 'Результатов более 10. Показаны первые 10\n\n'
                break
        text += 'Результат по вашему запросу:'
        bot.send_message(message.chat.id, text, reply_markup=markup)


bot.polling(none_stop=True, interval=0, timeout=20)