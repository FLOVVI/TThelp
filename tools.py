from telebot import types
import os
import random

import config


def main_menu(markup):
    for i in ['Важное', 'Гарантии Сертификаты', 'Возвраты', 'Номера', 'Настройки', 'ОСС']:
        markup.add(types.InlineKeyboardButton(f'🗂 Категория: {i}', callback_data=i))

    return markup


def number_delete(word):
    word = word.replace('1. ', '').replace('2. ', '').replace('3. ', '').replace('4. ', '').replace('5. ', '')
    word = word.replace('6. ', '').replace('7. ', '').replace('8. ', '').replace('9. ', '')
    return word


def add_text(word, search):
    if word in [i[0] for i in search.get_folders()]:
        word = f'🗂 Категория: {word}'
    else:
        if word != 'Ничего не найдено':
            word = f'📄: {word}'
    return word


def result_processing(word, search):
    word = word.replace('.txt', '')
    url = word
    word = number_delete(word)
    word = add_text(word, search)
    return word, url


def get_salon(markup, database):
    for i in range(0, len(database.get_salon()), 3):
        try:
            markup.add(
                types.InlineKeyboardButton(database.get_salon()[i], callback_data=database.get_salon()[i]),
                types.InlineKeyboardButton(database.get_salon()[i+1], callback_data=database.get_salon()[i+1]),
                types.InlineKeyboardButton(database.get_salon()[i+2], callback_data=database.get_salon()[i+2])
                )
        except:
            markup.add(
                types.InlineKeyboardButton(database.get_salon()[i], callback_data=database.get_salon()[i]),
                types.InlineKeyboardButton(database.get_salon()[i + 1], callback_data=database.get_salon()[i + 1]),
            )
    return markup


def get_job_title(markup):
    markup.add(
        types.InlineKeyboardButton('РТТ', callback_data='РТТ'),
        types.InlineKeyboardButton('МПП', callback_data='МПП'),
        types.InlineKeyboardButton('Cтажер', callback_data='Стажер'),
    )
    return markup


def delete_files(user_id, group=None):
    if user_id == 'bot':
        dir_ = f'Mail\\{user_id}\\{group}'
    else:
        dir_ = f'Mail\\{user_id}'

    files_to_remove = [os.path.join(dir_, f) for f in os.listdir(dir_)]
    for f in files_to_remove:
        os.remove(f)

    if len(files_to_remove) != 0:
        return True
    else:
        return False


def get_files(user_id):
    dir_ = f'Mail\\{user_id}'
    files = []
    for i in os.listdir(dir_):
        files.append(i)
    if len(files) != 0:
        return ', '.join(files)
    else:
        return 'Отсуствуют'


# Кнопки категории для рассылки
def get_mailing_group_button(markup, user):
    if user == config.owner:
        markup.add(types.InlineKeyboardButton('ApSa', callback_data='ApSa'))
    markup.add(types.InlineKeyboardButton('ОСС', callback_data='ОСС'))
    markup.add(types.InlineKeyboardButton('Xiaomi', callback_data='Xiaomi'))
    markup.add(types.InlineKeyboardButton('Офис', callback_data='Офис'))
    markup.add(types.InlineKeyboardButton("Мхитарян", callback_data="Мхитарян"))
    markup.add(types.InlineKeyboardButton("Акимова", callback_data="Акимова"))
    markup.add(types.InlineKeyboardButton("Коптенкова", callback_data="Коптенкова"))
    return markup


def get_bot_files(group):
    dir_ = f'Mail\\bot\\{group}'
    files = []
    for i in os.listdir(dir_):
        files.append(i)
    return files


def apple_price_processing(file_name):
    if 'Apple' in file_name.split():
        file_name = file_name.split()
        file_name = f'{file_name[0]} {file_name[1]}.xls'
        return file_name
    else:
        return file_name


def generate_code():
    letters = '123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    while True:
        code = ''
        # Создаем 18-и значный код
        for i in range(8):
            code += random.choice(letters)
        break
    return code