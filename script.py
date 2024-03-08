import sqlite3
'''
Код для создания БД sqlite3

'''
connection = sqlite3.connect('user_of_bot.db')
cur = connection.cursor()
query = '''
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    subject TEXT,
    level TEXT,
    question TEXT,
    answer TEXT
);
'''
cur.execute(query)
connection.close()
