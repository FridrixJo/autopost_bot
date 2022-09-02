import sqlite3


class UsersDB:
    def __init__(self, db_file):
        self.db = sqlite3.connect(db_file, check_same_thread=False)
        self.sql = self.db.cursor()

    def close(self):
        self.db.close()

    def user_exists(self, user_id):
        try:
            result = self.sql.execute("SELECT `id` FROM `users` WHERE `user_id` = ?", (user_id,))
            return bool(len(result.fetchall()))
        except Exception as s:
            print(s, "user_exists")

    def add_user(self, user_id, name):
        try:
            self.sql.execute("INSERT INTO `users` (`user_id`, `name`) VALUES (?, ?)", (user_id, name))
        except Exception as e:
            print(e, "add_user")
        return self.db.commit()

    def get_users(self):
        try:
            result = self.sql.execute("SELECT `user_id` FROM `users`")
            return result.fetchall()
        except Exception as s:
            print(type(s))

    def get_users_by_type(self, type):
        try:
            result = self.sql.execute("SELECT `user_id` FROM `users` WHERE type = ?", (type,))
            return result.fetchall()
        except Exception as s:
            print(type(s))

    def get_users_by_admin_right(self, admin_right):
        try:
            result = self.sql.execute("SELECT `user_id` FROM `users` WHERE admin = ?", (admin_right,))
            return result.fetchall()
        except Exception as s:
            print(type(s))

    def delete_user(self, user_id):
        try:
            self.sql.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
        except Exception as e:
            pass
        return self.db.commit()

    def delete_all(self):
        user_list = self.get_users()
        print(user_list)
        try:
            for i in user_list:
                self.delete_user(i[0])
        except Exception as e:
            print(e)
        return self.db.commit()

    def set_name(self, user_id, name):
        try:
            self.sql.execute("UPDATE `users` SET name = ? WHERE user_id = ?", (name, user_id))
        except Exception as e:
            print(e, "name")
        return self.db.commit()

    def get_name(self, user_id):
        try:
            result = self.sql.execute("SELECT name FROM users WHERE user_id = ?", (user_id,))
            return result.fetchall()[0][0]
        except Exception as e:
            print(e, "get_name")

    def set_active(self, user_id, active):
        try:
            self.sql.execute("UPDATE `users` SET active = ? WHERE user_id = ?", (active, user_id))
        except Exception as e:
            print(e, "active")
        return self.db.commit()

    def get_active(self, user_id):
        try:
            result = self.sql.execute("SELECT active FROM users WHERE user_id = ?", (user_id,))
            return result.fetchall()[0][0]
        except Exception as e:
            print(e, "get_active")

    def set_minutes(self, user_id, minutes):
        try:
            self.sql.execute("UPDATE `users` SET minutes = ? WHERE user_id = ?", (minutes, user_id))
        except Exception as e:
            print(e, "minutes")
        return self.db.commit()

    def get_minutes(self, user_id):
        try:
            result = self.sql.execute("SELECT minutes FROM users WHERE user_id = ?", (user_id,))
            return result.fetchall()[0][0]
        except Exception as e:
            print(e, "get_minutes")
