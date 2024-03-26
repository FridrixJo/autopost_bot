import sqlite3


class ChatsDB:
    def __init__(self, db_file):
        self.db = sqlite3.connect(db_file, check_same_thread=False)
        self.sql = self.db.cursor()

    def close(self):
        self.db.close()

    def chat_exists(self, user_id, chat_id):
        try:
            result = self.sql.execute("SELECT `id` FROM `chats` WHERE `user_id` = ? AND `chat_id` = ?", (user_id, chat_id,))
            return bool(len(result.fetchall()))
        except Exception as s:
            print(s, "chat_exists")

    def add_chat(self, user_id, chat_id):
        try:
            self.sql.execute("INSERT INTO `chats` (`user_id`, `chat_id`) VALUES (?, ?)", (user_id, chat_id))
        except Exception as e:
            print(e, "add_chat")
        return self.db.commit()

    def get_chats_by_user(self, user_id):
        try:
            print(user_id)
            print("get_chats_by_user")
            result = self.sql.execute("SELECT `chat_id` FROM `chats` WHERE user_id = ?", (user_id,))
            res = result.fetchall()
            print(res)
            return res
        except Exception as s:
            print(type(s))

    def delete_chat(self, user_id, chat_id):
        try:
            self.sql.execute("DELETE FROM chats WHERE user_id = ? AND chat_id = ?", (user_id, chat_id))
        except Exception as e:
            print('delete_chat')
        return self.db.commit()

