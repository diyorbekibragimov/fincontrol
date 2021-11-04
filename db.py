import psycopg2
from functions.converter import RealTimeCurrencyConverter
from config import (URL, DB_NAME, DB_PASSWORD, DB_USER, DB_HOST)

class BotDB:

    def __init__(self):
        self.conn = psycopg2.connect(
                host=DB_HOST,
                database=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD
            )
        self.cursor = self.conn.cursor()
        self.converter = RealTimeCurrencyConverter(URL)

    def user_exists(self, user_id):
        self.cursor.execute("SELECT id FROM users WHERE user_id = ('%s')", (user_id,))
        return bool(len(self.cursor.fetchall()))

    def get_user_id(self, user_id):
        self.cursor.execute("SELECT id FROM users WHERE user_id = ('%s')", (user_id,))
        return self.cursor.fetchone()[0]

    def add_user(self, user_id, main_currency):
        self.cursor.execute("INSERT INTO users (user_id, main_currency) VALUES ('%s', '%s')", (user_id, main_currency))
        return self.conn.commit()
    
    def get_user_currency(self, user_id):
        self.cursor.execute("SELECT main_currency FROM users WHERE user_id = ('%s')", (user_id,))
        self.cursor.execute("SELECT id, name, shortcut, exrate FROM currencies WHERE id = ('%s')", (self.cursor.fetchone()[0],))
        return self.cursor.fetchone()

    def convert_all_records(self, user_id, prev_exrate, new_exrate, currency):
        values = self.cursor.execute("SELECT id, value FROM records WHERE user_id = ('%s')", (user_id,))
        values = self.cursor.fetchall()
        for v in values:
            v = tuple(v)
            updatedValue = self.converter.convert(prev_exrate, new_exrate, v[1])
            self.cursor.execute("UPDATE records SET value = '%s', currency = '%s' WHERE id = '%s'", (updatedValue, currency, v[0]))
        self.conn.commit()
    
    def edit_currency(self, user_id, main_currency, prev_exrate, new_exrate):
        self.cursor.execute("UPDATE users SET main_currency = '%s' WHERE user_id = '%s'", (main_currency, user_id))
        self.conn.commit()
        self.cursor.execute("SELECT id FROM users WHERE user_id = '%s'", (user_id,))
        self.convert_all_records(self.cursor.fetchone()[0], prev_exrate, new_exrate, main_currency)

    def add_record(self, user_id, operation, value):
        currency = self.get_user_currency(user_id)
        currency_id = currency[0]
        self.cursor.execute("INSERT INTO records (user_id, operation, value, currency) VALUES ('%s', '%s', '%s', '%s')", 
            (self.get_user_id(user_id),
            operation == "+",
            value,
            currency_id))
        return self.conn.commit()

    def get_main_records(self, user_id):
        context = {}
        self.cursor.execute("SELECT operation, value FROM records WHERE user_id = '%s' AND date BETWEEN datetime('now', 'start of day') AND datetime('now', 'localtime') ORDER BY date",
                (self.get_user_id(user_id),))
        context["day"] = self.cursor.fetchall()
        self.cursor.execute("SELECT operation, value FROM records WHERE user_id = '%s' AND date BETWEEN datetime('now', '-6 days') AND datetime('now', 'localtime') ORDER BY date",
                (self.get_user_id(user_id),))
        context["week"] = self.cursor.fetchall()
        self.cursor.execute("SELECT operation, value FROM records WHERE user_id = '%s' AND date BETWEEN datetime('now', 'start of month') AND datetime('now', 'localtime') ORDER BY date",
                (self.get_user_id(user_id),))
        context["month"] =  self.cursor.fetchall()
        return context
        
    def get_records(self, user_id, within = "*"):
        if (within == "day"):
            self.cursor.execute("SELECT * FROM records WHERE user_id = '%s' AND date BETWEEN datetime('now', 'start of day') AND datetime('now', 'localtime') ORDER BY date",
                (self.get_user_id(user_id),))
        elif(within == "week"):
            self.cursor.execute("SELECT * FROM records WHERE user_id = '%s' AND date BETWEEN datetime('now', '-6 days') AND datetime('now', 'localtime') ORDER BY date",
                (self.get_user_id(user_id),))
        elif (within == "month"):
            self.cursor.execute("SELECT * FROM records WHERE user_id = '%s' AND date BETWEEN datetime('now', 'start of month') AND datetime('now', 'localtime') ORDER BY date",
                (self.get_user_id(user_id),))
        elif (within == "year"):
            self.cursor.execute("SELECT * FROM records WHERE user_id = '%s' AND date BETWEEN datetime('now', 'start of year') AND datetime('now', 'localtime') ORDER BY date",
                (self.get_user_id(user_id),))
        else:
            self.cursor.execute("SELECT * FROM records WHERE user_id = '%s' ORDER BY date",
                (self.get_user_id(user_id),))

        return self.cursor.fetchall()

    def close(self):
        self.conn.close()