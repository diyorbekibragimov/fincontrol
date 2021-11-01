import sqlite3
from functions.converter import RealTimeCurrencyConverter
from config import URL

class BotDB:

    def __init__(self, db_file):
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()
        self.converter = RealTimeCurrencyConverter(URL)

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
        currency = self.cursor.execute("SELECT `id`, `name`, `shortcut`, `exrate` FROM `currencies` WHERE `id` = ?", (result.fetchone()[0],))
        return currency.fetchone()

    def convert_all_records(self, user_id, prev_exrate, new_exrate, currency):
        values = self.cursor.execute("SELECT `id`, `value` FROM `records` WHERE `user_id` = ?", (user_id,)).fetchall()
        for v in values:
            v = tuple(v)
            updatedValue = self.converter.convert(prev_exrate, new_exrate, v[1])
            self.cursor.execute("UPDATE `records` SET `value` = ?, `currency` = ? WHERE `id` = ?", (updatedValue, currency, v[0]))
        self.conn.commit()
    
    def edit_currency(self, user_id, main_currency, prev_exrate, new_exrate):
        self.cursor.execute("UPDATE `users` SET `main_currency` = ? WHERE `user_id` = ?", (main_currency, user_id))
        self.conn.commit()
        user_real_id = self.cursor.execute("SELECT `id` FROM `users` WHERE `user_id` = ?", (user_id,)).fetchone()[0]
        self.convert_all_records(user_real_id, prev_exrate, new_exrate, main_currency)

    def add_record(self, user_id, operation, value):
        currency = self.get_user_currency(user_id)
        currency_id = currency[0]
        self.cursor.execute("INSERT INTO `records` (`user_id`, `operation`, `value`, `currency`) VALUES (?, ?, ?, ?)", 
            (self.get_user_id(user_id),
            operation == "+",
            value,
            currency_id))
        return self.conn.commit()

    def get_main_records(self, user_id):
        context = {}
        first = self.cursor.execute("SELECT `operation`, `value` FROM `records` WHERE `user_id` = ? AND `date` BETWEEN datetime('now', 'start of day') AND datetime('now', 'localtime') ORDER BY `date`",
                (self.get_user_id(user_id),))
        context["day"] = first.fetchall()
        second =  self.cursor.execute("SELECT `operation`, `value` FROM `records` WHERE `user_id` = ? AND `date` BETWEEN datetime('now', '-6 days') AND datetime('now', 'localtime') ORDER BY `date`",
                (self.get_user_id(user_id),))
        context["week"] = second.fetchall()
        third = self.cursor.execute("SELECT `operation`, `value` FROM `records` WHERE `user_id` = ? AND `date` BETWEEN datetime('now', 'start of month') AND datetime('now', 'localtime') ORDER BY `date`",
                (self.get_user_id(user_id),))
        context["month"] =  third.fetchall()
        return context
        
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