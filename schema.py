import psycopg2

conn = psycopg2.connect(
            host="ec2-34-197-135-44.compute-1.amazonaws.com",
            database="dvt0dqabeoki7",
            user="gueqcdudjujspp",
            password="b8867f46533c04ba69ca1c5aa175132c7a93bcfe7be95bb8b567d4601450d984"
        )
cursor = conn.cursor()
# i = 1
# context = ["Uzbekistan", "USA", "Kyrgyzystan"]
# for i in range(len(context)):
#     cursor.execute("INSERT INTO countries(id, name) VALUES (%d, '%s')" % (i + 1, context[i]))
# conn.commit()

# context = [["Американский доллар", 2, "USD", "доллар"], ["Узбекский сум", 1, "UZS", "сум",], ["Киргизский сом", 3, "KGS", "сом"]]
# for i in range(len(context)):
#     cursor.execute("INSERT INTO currencies(id, name, country, exrate, shortcut) VALUES (%d, '%s', %d, '%s', '%s')" % (i + 1, context[i][0], 
#                     context[i][1], context[i][2], context[i][3]))
# cursor.execute("CREATE TABLE records (id SERIAL PRIMARY KEY, operation BOOLEAN NOT NULL, value DECIMAL NOT NULL, date TIMESTAMP NOT NULL DEFAULT Now(), currency INTEGER NOT NULL, user_id INTEGER NOT NULL, FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE, FOREIGN KEY(currency) REFERENCES currencies(id) ON DELETE SET NULL)")
# conn.commit()
# cursor.execute("CREATE TABLE countries (id SERIAL PRIMARY KEY, name VARCHAR(50) NOT NULL UNIQUE)")
# conn.commit()

# cursor.execute("CREATE TABLE currencies (" \
#         "id	SERIAL PRIMARY KEY," \
#         "name VARCHAR(100) NOT NULL UNIQUE," \
#         "country	INTEGER NOT NULL," \
#         "shortcut	VARCHAR(10)," \
#         "exrate	VARCHAR(3) NOT NULL UNIQUE," \
#         "FOREIGN KEY(country) REFERENCES countries(id) ON DELETE CASCADE )"
#     )
# conn.commit()

# cursor.execute("CREATE TABLE users (" \
#                 "id SERIAL PRIMARY KEY," \
#                 "user_id	INTEGER UNIQUE," \
#                 "join_date	TIMESTAMP NOT NULL DEFAULT Now()," \
#                 "main_currency	INTEGER NOT NULL DEFAULT 1," \
#                 "country	INTEGER," \
#                 "location	VARCHAR(255)," \
#                 "FOREIGN KEY(main_currency) REFERENCES currencies(id) ON DELETE CASCADE )"
#             )
# conn.commit()