import mysql.connector


class UserDatabaseInfo:
    """
    Класс UserDatabaseInfo реализует функционал работы с базой данных.
    """

    def __init__(self, password_sql, host_sql, user_for_sql, database_sql,
                 sql_port):
        self.password_sql = password_sql
        self.host_sql = host_sql
        self.user_for_sql = user_for_sql
        self.database_sql = database_sql
        self.port_sql = sql_port

    def connection_mysql(self):
        """
            Функция подключения к базе данных
        """
        connection = mysql.connector.connect(host=self.host_sql,
                                             port=self.port_sql,
                                             user=self.user_for_sql,
                                             password=self.password_sql,
                                             database=self.database_sql)
        return connection

    def check_in_database(self, user_id):
        """
                Функция проверки пользователя в базе данных
            """
        with self.connection_mysql() as connection:
            cursor = connection.cursor()
            query = "SELECT * FROM users WHERE user_id = %s"
            cursor.execute(query, (user_id, ))
            user_exists = cursor.fetchone()
            if user_exists:
                print("пользователь есть в базе данных")
                return True
            else:
                return False

    def add_to_database(self, user_id):
        """
                Функция добавления пользователя в базу данных
            """
        with self.connection_mysql() as connection:
            cursor = connection.cursor()
            # Если пользователя нет в базе, добавляем его
            query = "INSERT INTO users (user_id) VALUES (%s)"
            cursor.execute(query, (user_id, ))
            connection.commit()
            print("Юзер добавлен в базу данных")
