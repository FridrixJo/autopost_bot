import sqlite3


class ShopsDB:
    def __init__(self, db_file):
        self.db = sqlite3.connect(db_file, check_same_thread=False)
        self.sql = self.db.cursor()

    def close(self):
        self.db.close()

    def shop_exists(self, user_id, name):
        try:
            result = self.sql.execute("SELECT `id` FROM `stores` WHERE `user_id` = ? AND `name` = ?", (user_id, name))
            return bool(len(result.fetchall()))
        except Exception as s:
            print(s, "shop_exists")

    def add_shop(self, user_id, shop_id, name, description, pic_type, picture, tagged=0):
        try:
            self.sql.execute("INSERT INTO `stores` (`user_id`, `shop_id`, `name`, `description`, `pic_type`, `picture`, `tagged`) VALUES (?, ?, ?, ?, ?, ?, ?)", (user_id, shop_id, name, description, pic_type, picture, tagged))
        except Exception as e:
            print(e, "add_shop")
        return self.db.commit()

    def get_shop_id(self, user_id, name):
        try:
            result = self.sql.execute("SELECT shop_id FROM stores WHERE user_id = ? AND name = ?", (user_id, name,))
            return result.fetchall()[0][0]
        except Exception as e:
            print(e, "get_shop_id")

    def delete_shop(self, shop_id):
        try:
            self.sql.execute("DELETE FROM stores WHERE shop_id = ?", (shop_id,))
        except Exception as e:
            print('delete_shop')
        return self.db.commit()

    def edit_shop_name(self, shop_id, shop_name):
        try:
            self.sql.execute("UPDATE `stores` SET name = ? WHERE shop_id = ?", (shop_name, shop_id))
        except Exception as e:
            print(e, "edit_shop_name")
        return self.db.commit()

    def get_shop_name(self, shop_id):
        try:
            result = self.sql.execute("SELECT name FROM stores WHERE shop_id = ?", (shop_id,))
            return result.fetchall()[0][0]
        except Exception as e:
            print(e, "get_shop_name")

    def get_all_shops_by(self, param, sql_param):
        try:
            result = self.sql.execute(f"SELECT name FROM stores WHERE {sql_param} = ?", (param,))
            return result.fetchall()
        except Exception as e:
            print(e, "get_all_shops_by")

    def edit_shop_description(self, shop_id, description):
        try:
            self.sql.execute("UPDATE `stores` SET description = ? WHERE shop_id = ?", (description, shop_id))
        except Exception as e:
            print(e, "edit_shop_description")
        return self.db.commit()

    def get_shop_description(self, shop_id):
        try:
            result = self.sql.execute("SELECT description FROM stores WHERE shop_id = ?", (shop_id,))
            return result.fetchall()[0][0]
        except Exception as e:
            print(e, "get_shop_description")

    def edit_shop_picture(self, shop_id, picture):
        try:
            self.sql.execute("UPDATE `stores` SET picture = ? WHERE shop_id = ?", (picture, shop_id))
        except Exception as e:
            print(e, "edit_shop_picture")
        return self.db.commit()

    def get_shop_picture(self, shop_id):
        try:
            result = self.sql.execute("SELECT picture FROM stores WHERE shop_id = ?", (shop_id,))
            return result.fetchall()[0][0]
        except Exception as e:
            print(e, "get_shop_picture")

    def edit_shop_pic_type(self, shop_id, pic_type):
        try:
            self.sql.execute("UPDATE `stores` SET pic_type = ? WHERE shop_id = ?", (pic_type, shop_id))
        except Exception as e:
            print(e, "edit_shop_pic_type")
        return self.db.commit()

    def get_shop_pic_type(self, shop_id):
        try:
            result = self.sql.execute("SELECT pic_type FROM stores WHERE shop_id = ?", (shop_id,))
            return result.fetchall()[0][0]
        except Exception as e:
            print(e, "get_shop_pic_type")

    def edit_shop_tagged(self, shop_id, tagged):
        try:
            self.sql.execute("UPDATE `stores` SET tagged = ? WHERE shop_id = ?", (tagged, shop_id))
        except Exception as e:
            print(e, "edit_shop_pic_type")
        return self.db.commit()

    def get_shop_tagged(self, shop_id):
        try:
            result = self.sql.execute("SELECT tagged FROM stores WHERE shop_id = ?", (shop_id,))
            return result.fetchall()[0][0]
        except Exception as e:
            print(e, "get_shop_tagged")



