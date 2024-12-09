import telebot
from telebot import types
import config
from database import Database
import tools

bot = telebot.TeleBot(config.logs_token)


class Logger:
    def __init__(self, user):
        self.user = user
        self.database = Database(user)
        self.employee = self.database.get_employee()
        self.owner = config.owner

    def start_registration(self):
        bot.send_message(self.owner, f'{self.database.get_employee().username} Начал регистрацию')

    def successful_registration(self):
        bot.send_message(self.owner, f'{self.employee.username}\n'
                                     f'Прошел регистрацию: \n{self.database.get_employee_info()}\n\n')

    def send_mail(self):
        subject = self.database.get_mail().subject
        subject = subject if subject is not None else 'Отсуствует'
        bot.send_message(self.owner, f'{self.database.get_employee().username} Отправил письмо: \n'
                                     f'Получатель: {self.database.get_mail().recipient}\n'
                                     f'Тема: {subject}\n'
                                     f'Текст письма: {self.database.get_mail().message}\n'
                                     f'Вложенные файлы: {tools.get_files(self.user)}')

    def value_error(self, req, error):
        bot.send_message(self.owner, f"Отправлен недопустимый запрос:\n"
                                     f"Отправитель: {self.database.get_employee().username}\n"
                                     f"Запрос: {req}\n"
                                     f"Ошибка: ValueError:{error}")

    def bot_save_file(self, file_name, group):
        bot.send_message(self.owner, f'Бот сохранил файл: {file_name}\nФайлы в директории бота: {tools.get_bot_files(group)}')

    def bot_send_mail(self, group):
        bot.send_message(self.owner, f'Бот отправляет файлы: {tools.get_bot_files(group)} на {self.database.get_mail().recipient}')