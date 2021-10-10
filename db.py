import sqlite3
from aiogram.types import user

from dotenv import main

class BotDB:

    def __init__(self, db_file):
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()

    def user_exists(self, user_id):
        result = self.cursor.execute("SELECT `id` FROM `users` WHERE `user_id` = ?", (user_id,))
        return bool(len(result.fetchall()))

    def get_user_id(self, user_id):
        result = self.cursor.execute("SELECT `id` FROM `users` WHERE `user_id` = ?", (user_id,))
        return result.fetchone()[0]

    def add_user(self, user_id, main_currency):
        self.cursor.execute("INSERT INTO `users` (`user_id`, `main_currency`) VALUES (?, ?)", (user_id, main_currency))
        return self.conn.commit()
    
    def get_user_currency(self, user_id):
        result = self.cursor.execute("SELECT `main_currency` FROM `users` WHERE `user_id` = ?", (user_id,))
        currency = self.cursor.execute("SELECT `name` FROM `currencies` WHERE `id` = ?", (result.fetchone()[0],))
        return currency.fetchone()[0]
    
    def edit_currency(self, user_id, main_currency):
        self.cursor.execute("UPDATE `users` SET `main_currency` = ? WHERE `user_id` = ?", (main_currency, user_id))
        return self.conn.commit()

    def add_record(self, user_id, operation, value):
        self.cursor.execute("INSERT INTO `records` (`user_id`, `operation`, `value`) VALUES (?, ?, ?)", 
            (self.get_user_id(user_id),
            operation == "+",
            value))
        return self.conn.commit()
    
    def get_records(self, user_id, within = "*"):
        if (within == "day"):
            result = self.cursor.execute("SELECT * FROM `records` WHERE `user_id` = ? AND `date` BETWEEN datetime('now', 'start of day') AND datetime('now', 'localtime') ORDER BY `date`",
                (self.get_user_id(user_id),))
        elif(within == "week"):
            result = self.cursor.execute("SELECT * FROM `records` WHERE `user_id` = ? AND `date` BETWEEN datetime('now', '-6 days') AND datetime('now', 'localtime') ORDER BY `date`",
                (self.get_user_id(user_id),))
        elif (within == "month"):
            result = self.cursor.execute("SELECT * FROM `records` WHERE `user_id` = ? AND `date` BETWEEN datetime('now', 'start of month') AND datetime('now', 'localtime') ORDER BY `date`",
                (self.get_user_id(user_id),))
        elif (within == "year"):
            result = self.cursor.execute("SELECT * FROM `records` WHERE `user_id` = ? AND `date` BETWEEN datetime('now', 'start of year') AND datetime('now', 'localtime') ORDER BY `date`",
                (self.get_user_id(user_id),))
        else:
            result = self.cursor.execute("SELECT * FROM `records` WHERE `user_id` = ? ORDER BY `date`",
                (self.get_user_id(user_id),))

        return result.fetchall()

    def close(self):
        self.conn.close()