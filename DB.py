import sqlite3

def init_db():
    conn = sqlite3.connect('../botnikita.db')
    cursor = conn.cursor()
    # Удаляем таблицу, если она существует (это удалит все данные)
    cursor.execute('DROP TABLE IF EXISTS users')
    # Создаем таблицу заново
    cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            tg_id INTEGER UNIQUE,
            username TEXT,
            password TEXT,
            name TEXT,
            tariff TEXT
        )
    ''')
    conn.commit()
    conn.close()

def check_user_exists(tg_id):
    conn = sqlite3.connect('../botnikita.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE tg_id = ?', (tg_id,))
    user = cursor.fetchone()
    conn.close()
    return user

def check_credentials(username, password):
    conn = sqlite3.connect('../botnikita.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
    user = cursor.fetchone()
    conn.close()
    return user

def add_user(tg_id, username, name, password=None, tariff=None):
    conn = sqlite3.connect('../botnikita.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO users (tg_id, username, name, password, tariff) VALUES (?, ?, ?, ?, ?)', (tg_id, username, name, password, tariff))
    conn.commit()
    conn.close()
