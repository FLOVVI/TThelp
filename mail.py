import os
import time

import config
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from email.mime.base import MIMEBase
from email import encoders
from email.mime.multipart import MIMEMultipart
from database import Database
import tools


class Mail:
    def __init__(self, user):
        self.database = Database(user)
        self.login = config.mail_data['login']
        self.password = config.mail_data['password']

        self.smtpObj = smtplib.SMTP('smtp.gmail.com', 587)
        self.smtpObj.starttls()
        self.smtpObj.login(self.login, self.password)

    def get_data(self):
        return self.database.get_mail()

    def get_sender(self):
        return f'Отправитель: {self.database.get_employee().job_title} {self.database.get_employee().name}\n' \
               f'Салон: {self.database.get_salon_info(self.database.get_employee().salon)}'

    @staticmethod
    def get_mailing_group():
        return {'Проверка': ['flovvi78@gmail.com', 'flovvi8@gmail.com'],
                'ApSa': ['flovvi78@gmail.com'],
                'ОСС': ['tt@simvol71.ru'],
                'Xiaomi': ['tt_xiaomi@simvol71.ru'],
                'Офис': ['office@simvol71.ru'],
                "Мхитарян": [
                    "oss.al1@simvol71.ru",  # Алексин 1
                    "mi.kl@simvol71.ru",  # Калуга
                    "oss.kr2@simvol71.ru",  # Киреевск 2
                    "oss.kr3@simvol71.ru",  # Киреевск 3
                    "mi.al@simvol71.ru",  # Ми Алексин
                    "sg.nm@simvol71.ru",  # Новомосковск
                    "mi.sp@simvol71.ru",  # Серпухов
                    "oss.ya2@simvol71.ru",  # Ясногорск 2
                    "oss.ya1@simvol71.ru"  # Ясногорск 1
                ],
                "Акимова": [
                    "oss.bl1@simvol71.ru",  # Белёв 1
                    "oss.bl3@simvol71.ru",  # Белёв 3
                    "oss.bl4@simvol71.ru",  # Белёв 4
                    "oss.bg3@simvol71.ru",  # Богородицк 3
                    'mi.bg@simvol71.ru',  # Богородицк ЧГД
                    "oss.ef@simvol71.ru",  # Ефремов
                    "mi.kk@simvol71.ru",  # Куклы
                    "mi.ob@simvol71.ru",  # Обнинск
                    "oss.sv3@simvol71.ru",  # Суворов 3
                    "oss.sv4@simvol71.ru"  # Суворов 4
                ],
                "Коптенкова": [
                    "oss.ar2@simvol71.ru",  # Арсеньево 2
                    "oss.ar3@simvol71.ru",  # Арсеньево 3
                    "mi.pr@simvol71.ru",  # Демидовский
                    "oss.dn1@simvol71.ru",  # Донской
                    "oss.km3@simvol71.ru",  # Кимовск 3
                    "oss.km5@simvol71.ru",  # Кимовск 5
                    "mi.mx@simvol71.ru",  # Макси
                    "oss.od1@simvol71.ru",  # Одоев 1
                    "oss.od4@simvol71.ru",  # Одоев 4
                    "mi.sh@simvol71.ru"  # Щекино
                ]}

    def send_mail(self, add_from=True):
        data = self.database.get_mail()
        message = data.message
        subject = data.subject
        recipient = data.recipient

        if recipient in self.get_mailing_group():
            return self.send_mailing(recipient, add_from)
        elif recipient is None:
            return None

        else:
            file_names = [i for i in os.listdir(f'Mail\\{data.id}')]
            file_paths = [f'Mail\\{data.id}\\{i}' for i in file_names]

            # Создаем объект сообщения
            msg = MIMEMultipart()
            msg['Subject'] = Header(subject, 'utf-8')
            msg['From'] = self.login
            msg['To'] = recipient

            # Текст письма
            if add_from:
                if self.database.get_employee().job_title in ['РТТ', 'МПП', 'Стажер']:
                    message += f'\n\n{"-" * 33}\n\n{self.get_sender()}'
                    message += f'\n\nПожалуйста не отвечайте на данное сообщение!' \
                               f'\nДля связи используйте рабочую почту отправителя'

            else:
                message += f'\n\n{"-" * 33}\n\nС уважением техническая поддержка TTbot'

            msg.attach(MIMEText(message, 'plain', 'utf-8'))

            # Добавляем файл во вложение
            for i in range(len(file_paths)):
                file_path = file_paths[i]
                file_name = file_names[i]

                with open(file_path, 'rb') as file:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(file.read())
                    encoders.encode_base64(part)

                    # Добавляем заголовок с явным указанием имени файла
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename="{Header(file_name, "utf-8").encode()}"'
                    )
                    msg.attach(part)

            # Отправляем письмо
            self.smtpObj.sendmail(msg['From'], recipient, msg.as_string())
            self.database.save_mail(message=None, subject=None, recipient=None)
            tools.delete_files(data.id)
            if len(file_paths) != 0:
                return 'Письмо с вложениями успешно отправлено'
            else:
                return 'Письмо успешно отправлено'

    def send_mailing(self, mailing_group, add_from):
        data = self.database.get_mail()
        message = data.message
        subject = data.subject
        recipients = self.get_mailing_group()[mailing_group]

        if data.id == 'bot':
            file_names = [i for i in os.listdir(f'Mail\\{data.id}\\{mailing_group}')]
            file_paths = [f'Mail\\{data.id}\\{mailing_group}\\{i}' for i in file_names]
        else:
            file_names = [i for i in os.listdir(f'Mail\\{data.id}')]
            file_paths = [f'Mail\\{data.id}\\{i}' for i in file_names]

        for recipient in recipients:
            # Создаем объект сообщения
            msg = MIMEMultipart()
            msg['Subject'] = Header(subject, 'utf-8')
            msg['From'] = self.login
            msg['To'] = recipient
            # Текст письма
            if add_from:
                if self.database.get_employee().job_title in ['РТТ', 'МПП', 'Стажер']:
                    message += f'\n\n{"-" * 33}\n\n{self.get_sender()}'
                    message += f'\n\nПожалуйста не отвечайте на данное сообщение!' \
                               f'\nДля связи используйте рабочую почту отправителя'

            else:
                message += f'\n\n{"-" * 33}\n\nС уважением техническая поддержка TTbot'

            msg.attach(MIMEText(message, 'plain', 'utf-8'))

            # Добавляем файл во вложение
            for i in range(len(file_paths)):
                file_path = file_paths[i]
                file_name = file_names[i]

                with open(file_path, 'rb') as file:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(file.read())
                    encoders.encode_base64(part)

                    # Добавляем заголовок с явным указанием имени файла
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename="{Header(file_name, "utf-8").encode()}"'
                    )
                    msg.attach(part)

            # Отправляем письмо
            self.smtpObj.sendmail(msg['From'], recipient, msg.as_string())
        if data.id != 'bot':
            tools.delete_files(data.id, group=mailing_group)
        self.database.save_mail(message=None, subject=None, recipient=None)
        if len(file_paths) != 0:
            return 'Рассылка с вложениями успешно отправлена'
        else:
            return 'Рассылка успешно отправлена'
