import sqlite3


class Create:
    """
    @staticmethod
    def search_table():
        # Проверяем наличие таблицы
        connect = sqlite3.connect('TT.db')
        cursor = connect.cursor()


        check = cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' and name='main'"
        )

        if check.fetchone() is None:
            cursor.execute("CREATE TABLE employee ("
                           "id STRING PRIMARY KEY,"
                           "username STRING"
                           "process INT"
                           "name STRING,"
                           "salon STRING,)"
                           )

            cursor.execute("CREATE TABLE salon ("
                           "name STRING,"
                           "number INT,)"
                           )
    """
    @staticmethod
    def search_user(user_id):
        connect = sqlite3.connect('TT.db')
        cursor = connect.cursor()

        check = cursor.execute(
            "SELECT id FROM employee WHERE id = ?", (user_id,)
        )

        if check.fetchone() is None:
            cursor.execute("INSERT INTO employee VALUES (?, ?, ?, ?, ?)",
                           (user_id, None, 0, None, None,))

        connect.commit()
        connect.close()


class Database:
    def __init__(self, user):
        connect = sqlite3.connect('TT.db')
        cursor = connect.cursor()
        Create().search_user(user)

        self.user = user
        self.username = cursor.execute('SELECT username FROM employee WHERE id = ?', (self.user,)).fetchone()[0]
        self.process = cursor.execute('SELECT process FROM employee WHERE id = ?', (self.user,)).fetchone()[0]
        self.name = cursor.execute('SELECT name FROM employee WHERE id = ?', (self.user,)).fetchone()[0]
        self.salon = cursor.execute('SELECT salon FROM employee WHERE id = ?', (self.user,)).fetchone()[0]

    def get_salon(self):
        connect = sqlite3.connect('TT.db')
        cursor = connect.cursor()

        return [i[0] for i in cursor.execute('SELECT name FROM salon').fetchall()]

    def save(self, **kwargs):
        # name=key

        connect = sqlite3.connect('TT.db')
        cursor = connect.cursor()

        for key, value in kwargs.items():
            cursor.execute(f"UPDATE employee SET {key} = ? WHERE id = ?", (value, self.user))
        connect.commit()
        connect.close()