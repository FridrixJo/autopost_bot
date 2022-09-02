import sqlite3


class ContactsDB:
    def __init__(self, db_file):
        self.db = sqlite3.connect(db_file, check_same_thread=False)
        self.sql = self.db.cursor()

    def close(self):
        self.db.close()

    def contact_exists(self, shop_id, name):
        try:
            result = self.sql.execute("SELECT `id` FROM `contacts` WHERE `shop_id` = ? AND `name` = ?", (shop_id, name))
            return bool(len(result.fetchall()))
        except Exception as s:
            print(s, "contact_exists")

    def add_contact(self, shop_id, name, link):
        try:
            self.sql.execute("INSERT INTO `contacts` (`shop_id`, `name`, `link`) VALUES (?, ?, ?)", (shop_id, name, link))
        except Exception as e:
            print(e, "add_shop")
        return self.db.commit()

    def delete_contact(self, shop_id, name):
        try:
            self.sql.execute("DELETE FROM contacts WHERE shop_id = ? AND name = ?", (shop_id, name))
        except Exception as e:
            print('delete_contact')
        return self.db.commit()

    def edit_contact_name(self, shop_id, name, new_name):
        try:
            self.sql.execute("UPDATE `contacts` SET name = ? WHERE shop_id = ? AND name = ?", (new_name, shop_id, name))
        except Exception as e:
            print(e, "edit_contact_name")
        return self.db.commit()

    def edit_contact_link(self, shop_id, name, link):
        try:
            self.sql.execute("UPDATE `contacts` SET link = ? WHERE shop_id = ? AND name = ?", (link, shop_id, name))
        except Exception as e:
            print(e, "edit_contact_link")
        return self.db.commit()

    def get_contacts_by(self, param, sql_param):
        try:
            result = self.sql.execute(f"SELECT name FROM contacts WHERE {sql_param} = ?", (param,))
            return result.fetchall()
        except Exception as e:
            print(e, "get_contacts_by")

    def get_contact_name(self, shop_id, name):
        try:
            result = self.sql.execute("SELECT name FROM contacts WHERE shop_id = ? AND name = ?", (shop_id, name,))
            return result.fetchall()[0][0]
        except Exception as e:
            print(e, "get_contact_name")

    def get_contact_link(self, shop_id, name):
        try:
            result = self.sql.execute("SELECT link FROM contacts WHERE shop_id = ? AND name = ?", (shop_id, name,))
            return result.fetchall()[0][0]
        except Exception as e:
            print(e, "get_contact_link")
