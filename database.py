import sqlite3
from dataclasses import dataclass

database_name = 'TT.db'


@dataclass
class SalonInfo:
    name: str
    adress: str
    mail: str
    number: str
    employees: str
    tm: str


@dataclass
class Mail:
    id: str
    message: str
    subject: str
    recipient: str
    process: int


@dataclass()
class Employee:
    id: str
    username: str
    process: float
    name: str
    job_title: str
    salon: str



class Create:
    @staticmethod
    def search_user(user_id):
        connect = sqlite3.connect(database_name)
        cursor = connect.cursor()

        check = cursor.execute(
            "SELECT id FROM employee WHERE id = ?", (user_id,)
        )

        if check.fetchone() is None:
            cursor.execute("INSERT INTO employee VALUES (?, ?, ?, ?, ?, ?)",
                           (user_id, None, 0, None, None, None,))

        check = cursor.execute(
            "SELECT id FROM mail WHERE id = ?", (user_id,)
        )

        if check.fetchone() is None:
            cursor.execute("INSERT INTO mail VALUES (?, ?, ?, ?, ?)",
                           (user_id, None, None, None, None,))

        connect.commit()
        connect.close()


class Database:
    def __init__(self, user):
        connect = sqlite3.connect(database_name)
        cursor = connect.cursor()
        Create().search_user(user)

        self.user = user

    def get_salon(self):
        connect = sqlite3.connect(database_name)
        cursor = connect.cursor()

        return [i[0] for i in cursor.execute('SELECT name FROM salon').fetchall()]

    def get_salon_info(self, salon, get_dataclass=False):
        connect = sqlite3.connect(database_name)
        cursor = connect.cursor()

        name = salon
        address = cursor.execute('SELECT address FROM salon WHERE name = ?', (salon,)).fetchone()[0]
        mail = cursor.execute('SELECT mail FROM salon WHERE name = ?', (salon,)).fetchone()[0]
        number = cursor.execute('SELECT number FROM salon WHERE name = ?', (salon,)).fetchone()[0]
        tm = cursor.execute('SELECT tm FROM salon WHERE name = ?', (salon,)).fetchone()[0]

        employees = self.get_employees(salon)
        if employees is not None:
            employees = [f'\n{i[0][0]} {i[1][0]} (tg: {i[2][0]})' for i in employees]
            employees = ' '.join(employees)
        else:
            employees = 'Отсуствуют'
        if not get_dataclass:
            return f'{name}\nАдрес: {address}\nПочта: {mail}\nНомер: {number}\n' \
                   f'ТМ: {tm}\nСотрудники: {employees}'
        else:
            return SalonInfo(name=name, adress=address, mail=mail, number=number, employees=employees, tm=tm)

    def get_employees(self, salon):
        connect = sqlite3.connect(database_name)
        cursor = connect.cursor()

        emp = []

        name = cursor.execute('SELECT name FROM employee WHERE salon = ?', (salon,)).fetchall()
        job_title = cursor.execute('SELECT job_title FROM employee WHERE salon = ?', (salon,)).fetchall()
        username = cursor.execute('SELECT username FROM employee WHERE salon = ?', (salon,)).fetchall()

        for i in range(len(name)):
            emp.append([job_title[i], name[i], username[i]])

        for i in emp:
            # РТТ в начале, Стажер в конце
            if i[0][0] == 'РТТ':
                emp.remove(i)
                emp.insert(0, i)
            if i[0][0] == 'Стажер':
                emp.remove(i)
                emp.append(i)

        if len(name) == 0:
            return None
        else:
            return emp

    def get_employee(self):
        connect = sqlite3.connect(database_name)
        cursor = connect.cursor()

        username = cursor.execute('SELECT username FROM employee WHERE id = ?', (self.user,)).fetchone()[0]
        process = cursor.execute('SELECT process FROM employee WHERE id = ?', (self.user,)).fetchone()[0]
        name = cursor.execute('SELECT name FROM employee WHERE id = ?', (self.user,)).fetchone()[0]
        job_title = cursor.execute('SELECT job_title FROM employee WHERE id = ?', (self.user,)).fetchone()[0]
        salon = cursor.execute('SELECT salon FROM employee WHERE id = ?', (self.user,)).fetchone()[0]

        return Employee(id=self.user, username=username, process=process, name=name, job_title=job_title, salon=salon)

    def get_mail(self):
        connect = sqlite3.connect(database_name)
        cursor = connect.cursor()

        message = cursor.execute('SELECT message FROM mail WHERE id = ?', (self.user,)).fetchone()[0]
        subject = cursor.execute('SELECT subject FROM mail WHERE id = ?', (self.user,)).fetchone()[0]
        recipient = cursor.execute('SELECT recipient FROM mail WHERE id = ?', (self.user,)).fetchone()[0]
        process = cursor.execute('SELECT process FROM mail WHERE id = ?', (self.user,)).fetchone()[0]

        return Mail(id=self.user, message=message, subject=subject, recipient=recipient, process=process)

    def save_employee(self, **kwargs):
        connect = sqlite3.connect(database_name)
        cursor = connect.cursor()

        for key, value in kwargs.items():
            cursor.execute(f"UPDATE employee SET {key} = ? WHERE id = ?", (value, self.user))
        connect.commit()
        connect.close()

    def save_mail(self, **kwargs):
        connect = sqlite3.connect(database_name)
        cursor = connect.cursor()

        for key, value in kwargs.items():
            cursor.execute(f"UPDATE mail SET {key} = ? WHERE id = ?", (value, self.user))
        connect.commit()
        connect.close()

    def get_employee_info(self, job_title=True):
        text = f'{self.get_employee().name} (tg: {self.get_employee().username})'
        if job_title:
            text += f'\n{self.get_employee().job_title} в {self.get_employee().salon}'
        else:
            text += f'\nСалон: {self.get_employee().salon}'
        return text
