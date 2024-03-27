"""
Этот модуль содержит класс Bot, реализующий функционал бота для ВКонтакте.
"""

import time
import traceback

import vk_api
from vk_api.longpoll import VkEventType, VkLongPoll
from vk_api.utils import get_random_id
from commands import commands_list
from config.config import THIRD_PARTY_ID, THIRD_PARTY_ID_TWO, GROUP_LINK, TOKEN, PASSWORD_SQL, SQL_PORT, HOST_SQL, USER_SQL, DATABASE_SQL
from user.user_manager import UserManager
from user.user_blocker import UserBlocker
from user.spam_checker import SpamCheckerManager
from user.user_database import UserDatabaseInfo


class Bot:
    """
    Класс Bot реализует функционал бота для ВКонтакте.
    """

    def __init__(self, token: str, user_blocker: UserBlocker,
                 spam_checker: SpamCheckerManager, user_manager: UserManager,
                 database: UserDatabaseInfo):
        self.token = token
        self.vk_session = vk_api.VkApi(token=self.token)
        self.vk = self.vk_session.get_api()
        self.longpoll = VkLongPoll(self.vk_session)
        self.spam_checker = spam_checker
        self.user_blocker = user_blocker
        self.user_manager = user_manager
        self.database = database

    def generate_dialog_link(self, user_id):
        """
        Генерирует ссылку на диалог с пользователем.
        """
        return f'{GROUP_LINK}={user_id}'

    def send_message_to_user(self, user_id, message):
        """
        Отправляет сообщение пользователю
        """
        self.vk.messages.send(
            user_id=user_id,
            random_id=get_random_id(),
            message=message,
        )

    def message_from_admin(self, user_id, admin_id):
        """
        Отправка сообщения администратору.
        """
        dialog_link = self.generate_dialog_link(user_id)
        message_from_admin = (
            f"&#128276; Пользователь вызывает администратора через сообщение сообщества. "
            f"Ссылка на диалог: {dialog_link}")
        self.send_message_to_user(admin_id, message_from_admin)

    def message_to_admin_and_user(self, user_id, admin_id, message):
        """
        Отправляет сообщение администратору и пользователю.
        """
        self.message_from_admin(user_id, admin_id)
        self.send_message_to_user(user_id, message)

    def handler_user_message(self, user_id, message, commands_list):
        """
        Обрабатывает сообщение от пользователя.
        """
        if message == '/adt':
            self.message_to_admin_and_user(user_id, THIRD_PARTY_ID,
                                           commands_list[message])
        elif message == '/adc':
            self.message_to_admin_and_user(user_id, THIRD_PARTY_ID_TWO,
                                           commands_list[message])
        elif message == '/admin':
            self.send_message_to_user(user_id, commands_list[message])
        else:
            self.send_message_to_user(user_id, commands_list[message])

    def handle_event(self, event):
        """
        Обрабатывает событие от ВКонтакте.
        """
        if event.type == VkEventType.MESSAGE_NEW:
            user_id = event.user_id
            message = event.text.lower()

            if not self.user_manager.exists(user_id):
                self.user_manager.add(user_id)

            if not self.database.check_user(
                    user_id) and message not in commands_list:
                self.database.add_user(user_id)
                self.send_message_to_user(user_id, commands_list['/info'])
            if message not in commands_list:
                return

            if not self.user_blocker.blocked_status(user_id):
                self.user_blocker.remove_ban_and_reset_attributes(
                    user_id, self.user_manager.fetch(user_id))

                if self.spam_checker.detect_spam(
                        self.user_manager.fetch(user_id)):
                    self.user_blocker.block_user(user_id)
                    self.send_message_to_user(
                        user_id,
                        'Вы заблокированы на минуту за спам командами')
                    return
                self.handler_user_message(user_id, message, commands_list)

    def run(self):
        """
        Запускает бота.
        """
        while True:
            try:
                for event in self.longpoll.listen():
                    self.handle_event(event)
            except (ConnectionError, vk_api.VkApiError) as e:
                traceback.print_exc()
                print(
                    f"Произошла ошибка: {e}. Бот будет перезапущен через 10 секунд."
                )
                time.sleep(10)
                continue


if __name__ == "__main__":
    sql_Database = UserDatabaseInfo(PASSWORD_SQL, HOST_SQL, USER_SQL,
                                    DATABASE_SQL, SQL_PORT)
    user_manager = UserManager()
    user_blocker = UserBlocker(user_manager)
    spam_checker = SpamCheckerManager(user_blocker, user_manager)
    bot = Bot(TOKEN, user_blocker, spam_checker, user_manager, sql_Database)
    bot.run()
