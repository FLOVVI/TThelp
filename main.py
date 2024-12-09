import time

import telebot
from telebot import types
import os
from datetime import datetime

import config
import tools

from database import Database
from search import Search
from send import Send
from mail import Mail
from logger import Logger

print("Active")
bot = telebot.TeleBot(config.token)


@bot.message_handler(func=lambda message: message.chat.id < 0)
def chat(message):
    if message.reply_to_message is not None and message.text == '@flwTT_bot':
        database = Database(message.reply_to_message.from_user.id)
        bot.reply_to(message, database.get_employee_info())


@bot.message_handler(commands=["start"])
def start(message):
    database = Database(message.from_user.id)
    if not os.path.exists(f'Mail\\{message.from_user.id}'):
        os.mkdir(f'Mail\\{message.from_user.id}')
    if message.from_user.username is not None or database.get_employee().username is not None:
        database.save_employee(username=f'@{message.from_user.username}', process=0)
        markup = types.InlineKeyboardMarkup()
        markup = tools.main_menu(markup)
        bot.send_message(message.chat.id, 'Напишите свой запрос или выберите категорию:', reply_markup=markup)

        if database.get_employee().name is None:
            bot.send_message(message.chat.id, 'Пожалуйста пройдите регистрацию:\n\n/registration')
    else:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        reg_button = types.KeyboardButton(text="Отправить номер телефона",
                                          request_contact=True)
        keyboard.add(reg_button)
        bot.send_message(message.chat.id, 'Чтобы продолжить отправьте ваш номер телефона.',
                         reply_markup=keyboard)


@bot.message_handler(content_types=['contact'])
def handle_contact(message):
    database = Database(message.from_user.id)
    database.save_employee(username=message.contact.phone_number, process=0)

    markup = types.InlineKeyboardMarkup()
    markup = tools.main_menu(markup)
    bot.send_message(message.chat.id, 'Напишите свой запрос или выберите категорию:', reply_markup=markup)

    if database.get_employee().name is None:
        bot.send_message(message.chat.id, 'Пожалуйста пройдите регистрацию:\n\n/registration', reply_markup=types.ReplyKeyboardRemove())


@bot.message_handler(commands=["registration"])
def registration(message):
    database = Database(message.from_user.id)
    logger = Logger(message.from_user.id)
    logger.start_registration()
    database.save_employee(process=1)
    bot.send_message(message.chat.id, f'Напишите ваше Ф.И. (Например: Иванов Иван)')


@bot.message_handler(commands=["salon_info"])
def salon_info(message):
    database = Database(message.from_user.id)
    database.save_employee(process=4)
    markup = types.InlineKeyboardMarkup()
    markup = tools.get_salon(markup, database)
    bot.send_message(message.chat.id, f'Выберите салон: ',
                     reply_markup=markup)


@bot.message_handler(commands=["send_mail"])
def send_mail(message):
    database = Database(message.from_user.id)
    if database.get_employee().name is not None:
        database.save_employee(process=5)
        markup = types.InlineKeyboardMarkup()
        if database.get_employee().salon == 'Офис' or message.from_user.id == config.owner:
            markup.add(types.InlineKeyboardButton('Отправить Рассылку', callback_data='mailing'))
        markup = tools.get_salon(markup, database)
        markup.add(types.InlineKeyboardButton('Написать почту вручную', callback_data='write_mail'))
        bot.send_message(message.chat.id, f'Выберите салон для отправки сообщения на почту: ',
                         reply_markup=markup)
    else:
        bot.send_message(message.chat.id, 'Сначала пройдите регистрацию:\n\n/registration')


@bot.message_handler(commands=["cancel"])
def cancel(message):
    database = Database(message.from_user.id)
    database.save_employee(process=0)
    database.save_mail(process=0)
    delete_files = tools.delete_files(message.from_user.id)
    if delete_files:
        bot.send_message(message.chat.id, 'Файлы удалены')
    bot.send_message(message.chat.id, 'Все процессы отменены')


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    database = Database(call.from_user.id)
    req = call.data
    logger = Logger(call.from_user.id)
    mail = Mail(call.from_user.id)

    # Меню
    if req == 'back':
        markup = types.InlineKeyboardMarkup()
        markup = tools.main_menu(markup)
        bot.edit_message_text('Результат по вашему запросу:', call.message.chat.id, call.message.message_id, reply_markup=markup)

    elif req == 'setting':
        bot.send_message(call.message.chat.id, 'Отправил информацию в поддержку.\n'
                                               'Дождитесь ответа в ближайшее время.')
        salon = call.message.text.split('\n')[0]
        bot.send_message(config.owner, f'{database.get_employee().username} Желает изменить данные {salon}')


    elif req == 'add_file':
        bot.send_message(call.message.chat.id, 'Отправьте файл для добавления в вложение\n\n'
                                               'Если файл не сохранился значит объем файла слишком большой')

    elif req == 'continue':
        database.save_mail(process=1)
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, 'Пожалуйста напишите текст письма:')

    elif req == 'other':
        markup = types.InlineKeyboardMarkup()
        markup = tools.get_job_title(markup)
        bot.edit_message_text('Напишите название вашей должности или укажите должность из предоставленных:',
                              call.message.chat.id, call.message.message_id, reply_markup=markup)
    elif req == 'write_mail':
        bot.delete_message(call.message.chat.id, call.message.message_id)
        database.save_mail(process=3)
        bot.send_message(call.message.chat.id, 'Пожалуйста напишите почту на которую нужно отправить сообщение\n'
                                               '(Обратите внимание: Почта должна заканчиваться на @simvol71.ru)')
    elif req == 'RTT2':
        bot.send_message(call.message.chat.id, 'Отправил информацию в поддержку.\n'
                                               'Не дожидаясь ответа нажмите на кнопку Верно или Изменить чтобы продолжить регистрацию.')
        bot.send_message(config.owner, f'{database.get_employee().username} является РТТ нескольких салонов\n'
                                       f'Вот так должно выглядеть: \n'
                                       f'1. id us proc name jt salon1, salon2\n'
                                       f'2. us name jt salon1\n'
                                       f'3. us name jt salon2\n')

    # Регистрация 1 этап
    elif database.get_employee().process == 1:
        bot.delete_message(call.message.chat.id, call.message.message_id)
        database.save_employee(salon=req, process=2)
        markup = types.InlineKeyboardMarkup()
        markup = tools.get_job_title(markup)
        markup.add(
            types.InlineKeyboardButton('Офис', callback_data='other'),
        )
        bot.send_message(call.message.chat.id, f'Укажите вашу должность: ', reply_markup=markup)

    # Регистрация 2 этап
    elif database.get_employee().process == 2:
        bot.delete_message(call.message.chat.id, call.message.message_id)
        database.save_employee(job_title=req, process=3)
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton('Верно', callback_data='right'),
            types.InlineKeyboardButton('Изменить', callback_data='wrong')
        )
        if req == 'РТТ':
            markup.add(types.InlineKeyboardButton('Я являюсь РТТ нескольких салонов', callback_data='RTT2'))
        bot.send_message(call.message.chat.id,
                         f'Вы {database.get_employee().name}\n{req} в {database.get_employee().salon}',
                         reply_markup=markup)

    # Регистрация 3 этап
    elif database.get_employee().process == 3:
        bot.delete_message(call.message.chat.id, call.message.message_id)
        if req == 'right':
            database.save_employee(process=0)
            logger.successful_registration()
            bot.send_message(call.message.chat.id, 'Данные успешно сохранены')
        if req == 'wrong':
            database.save_employee(process=1)
            bot.send_message(call.message.chat.id, f'Напишите ваше ФИ (Иванов Иван)')

    # Информация о салонах
    elif database.get_employee().process == 4:
        bot.delete_message(call.message.chat.id, call.message.message_id)
        markup = types.InlineKeyboardMarkup()
        if database.get_employee().job_title == 'ТМ' or call.from_user.id == config.owner:
            markup.add(types.InlineKeyboardButton('Изменить данные', callback_data='setting'))
        bot.send_message(call.message.chat.id, database.get_salon_info(req), reply_markup=markup)
        database.save_employee(process=0)

    # Отправка сообщения
    elif database.get_employee().process == 5:
        bot.delete_message(call.message.chat.id, call.message.message_id)
        database.save_mail(process=0)
        if req == 'right':
            database.save_employee(process=0)
            logger.send_mail()
            if database.get_mail().recipient == 'ApSa':
                database = Database('bot')
                subject = f'Apple и Samsung S {datetime.today().strftime("%d.%m.%Y")}'
                message = f'Актуальная информация про наличие, прайс Apple и прайс Samsung S на {datetime.today().strftime("%d.%m.%Y")}'
                database.save_mail(subject=subject, message=message, recipient='ApSa')
                mail = Mail('bot')
                bot.send_message(call.message.chat.id, mail.send_mail(add_from=False))
            else:
                bot.send_message(call.message.chat.id, mail.send_mail())
        elif req == 'wrong':
            database.save_employee(process=5)
            tools.delete_files(call.from_user.id)
            markup = types.InlineKeyboardMarkup()
            if database.get_employee().salon == 'Офис' or call.from_user.id == config.owner:
                markup.add(types.InlineKeyboardButton('Отправить Рассылку', callback_data='mailing'))
            bot.send_message(call.message.chat.id, f'Выберите салон для отправки сообщения на почту:',
                             reply_markup=tools.get_salon(markup, database))
        elif req == 'mailing':
            database.save_mail(process=5)
            markup = types.InlineKeyboardMarkup()
            markup = tools.get_mailing_group_button(markup, call.from_user.id)
            bot.send_message(call.message.chat.id, 'Выберите группу рассылки: ', reply_markup=markup)

        elif req == 'add_sub':
            database.save_mail(process=2)
            bot.send_message(call.message.chat.id, 'Пожалуйста напишите тему письма:')

        elif req in mail.get_mailing_group():
            database.save_mail(recipient=req, process=4)
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton('Продолжить', callback_data='continue'))
            bot.send_message(call.message.chat.id, 'Пожалуйста отправьте файлы для вложения.\n'
                                                   'Если таковых нет - нажмите Продолжить\n\n'
                                                   '❗️ Если файл не сохранился значит объем файла слишком большой',
                             reply_markup=markup)
        else:
            database.save_mail(recipient=database.get_salon_info(req, get_dataclass=True).mail, process=4)
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton('Продолжить', callback_data='continue'))
            bot.send_message(call.message.chat.id, 'Пожалуйста отправьте файлы для вложения.\n'
                                                   'Если таковых нет - нажмите Продолжить\n\n'
                                                   '❗️ Если файл не сохранился значит объем файла слишком большой', reply_markup=markup)

    # Поиск
    else:
        if req != 'Ничего не найдено':
            search = Search(None)
            send = Send(search.objects)
            send.get_request(req)
            markup = types.InlineKeyboardMarkup()
            count = 0
            text = ''
            if send.request_type == 1:
                for result in send.send_folder(req):
                    result, url = tools.result_processing(result, search)
                    markup.add(types.InlineKeyboardButton(result, callback_data=url))
                    count += 1
                    if count == 10:
                        text += 'Результатов более 10. Показаны первые 10\n\n'
                        break
                text += 'Результат по вашему запросу:'
                markup.add(types.InlineKeyboardButton(' ↪️ Назад', callback_data='back'))

                bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup)
            elif send.request_type == 2:
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton(' ↪️ Назад', callback_data='back'))
                bot.send_message(call.message.chat.id, send.send_file_text(req), reply_markup=markup)
            elif send.request_type == 3:
                bot.send_document(call.message.chat.id, send.send_document(req), visible_file_name=req)
        else:
            bot.send_message(call.message.chat.id, 'Пожалуйста напишите другой запрос')


@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    database = Database(message.from_user.id)
    if database.get_mail().process == 4:
        photo = message.photo[-1]
        file_info = bot.get_file(photo.file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        src = f'Mail\\{message.from_user.id}\\{tools.generate_code()}.jpg'
        print(src)
        with open(src, 'wb') as file:
            file.write(downloaded_file)

        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Продолжить', callback_data='continue'))

        bot.reply_to(message, f'Файл сохранен. Вы можете добавить еще файлы или продолжить регистрацию'
                              f'\n\nДля удаления напишите /cancel и начните процесс заполнения письма заново',
                     reply_markup=markup)



@bot.message_handler(content_types=['document', 'video'])
def handle_docs(message):
    if message.chat.id < 0:
        database = Database('bot')
        logger = Logger('bot')
        mail = Mail('bot')

        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        if 'Apple' in message.document.file_name.split() or 'Samsung' in message.document.file_name.split():
            file_name = tools.apple_price_processing(message.document.file_name)
            if file_name not in tools.get_bot_files('ApSa'):
                src = f'Mail\\bot\\ApSa\\' + file_name
                with open(src, 'wb') as file:
                    file.write(downloaded_file)
                logger.bot_save_file(file_name, 'ApSa')

            if len(tools.get_bot_files('ApSa')) == 3:
                subject = f'Apple и Samsung S {datetime.today().strftime("%d.%m.%Y")}'
                message = f'Актуальная информация про наличие, прайс Apple и прайс Samsung S на {datetime.today().strftime("%d.%m.%Y")}'
                database.save_mail(subject=subject, message=message, recipient='ApSa')
                # logger.bot_send_mail('ApSa')
                # mail.send_mail(add_from=False)

    else:
        database = Database(message.from_user.id)
        if database.get_mail().process == 4:
            file_info = bot.get_file(message.document.file_id)
            downloaded_file = bot.download_file(file_info.file_path)

            src = f'Mail\\{message.from_user.id}\\' + message.document.file_name
            with open(src, 'wb') as file:
                file.write(downloaded_file)

            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton('Продолжить', callback_data='continue'))

            bot.reply_to(message, f'Файл сохранен. Вы можете добавить еще файлы или продолжить регистрацию'
                                  f'\n\nДля удаления напишите /cancel и начните процесс заполнения письма заново', reply_markup=markup)


@bot.message_handler(content_types=["text"])
def handler_text(message):
    database = Database(message.from_user.id)
    logger = Logger(message.from_user.id)

    if database.get_employee().process == 1:
        database.save_employee(name=message.text)
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Офис', callback_data='Офис'))
        markup = tools.get_salon(markup, database)
        bot.send_message(message.chat.id, f'Укажите ваш салон:', reply_markup=markup)

    elif database.get_employee().process == 2:
        database.save_employee(job_title=message.text)
        bot.delete_message(message.chat.id, message.message_id)
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton('Верно', callback_data='right'),
            types.InlineKeyboardButton('Изменить', callback_data='wrong')
        )
        bot.send_message(message.chat.id,
                         f'Вы {database.get_employee().name}\n{message.text} в {database.get_employee().salon}',
                         reply_markup=markup)
        database.save_employee(process=3)

    elif database.get_employee().process == 5:
        if database.get_mail().process == 1:
            database.save_mail(message=message.text, process=0)
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton('Добавить тему письма', callback_data='add_sub'))
            markup.add(
                types.InlineKeyboardButton('Верно, Отправить!', callback_data='right'),
                types.InlineKeyboardButton('Изменить', callback_data='wrong')
            )
            bot.send_message(message.chat.id, f'Получатель: {database.get_mail().recipient}\n'
                                              f'Тема: Отсуствует\n'
                                              f'Текст письма: {message.text}\n'
                                              f'Вложенные файлы: {tools.get_files(message.from_user.id)}', reply_markup=markup)

        if database.get_mail().process == 2:
            database.save_mail(subject=message.text, process=0)
            markup = types.InlineKeyboardMarkup()
            markup.add(
                types.InlineKeyboardButton('Верно, Отправить!', callback_data='right'),
                types.InlineKeyboardButton('Изменить', callback_data='wrong')
            )
            bot.send_message(message.chat.id, f'Получатель: {database.get_mail().recipient}\n'
                                              f'Тема: {message.text}\n'
                                              f'Текст письма: {database.get_mail().message}\n'
                                              f'Вложенные файлы: {tools.get_files(message.from_user.id)}', reply_markup=markup)

        if database.get_mail().process == 3:
            if message.text.split('@')[-1] == 'simvol71.ru':
                database.save_mail(recipient=message.text, process=1)
                bot.send_message(message.chat.id, 'Пожалуйста напишите текст письма:')


    else:
        if message.text.title() in database.get_salon():
            bot.send_message(message.chat.id, database.get_salon_info(message.text.title()))

        else:
            try:
                markup = types.InlineKeyboardMarkup()
                count = 0
                search = Search(message.text)
                text = ''
                for result in search.result:
                    result, url = tools.result_processing(result, search)
                    markup.add(types.InlineKeyboardButton(result, callback_data=url))
                    count += 1
                    if count == 10:
                        text += 'Результатов более 10. Показаны первые 10\n\n'
                        break
                text += 'Результат по вашему запросу:'
                bot.send_message(message.chat.id, text, reply_markup=markup)
            except ValueError as error:
                logger.value_error(message.text, error)
                bot.send_message(message.chat.id, 'Данный запрос недоступен!\n')



bot.polling(none_stop=True, interval=0, timeout=20)
