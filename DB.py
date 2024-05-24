import sqlite3

def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            tg_id INTEGER UNIQUE,
            username TEXT,
            password TEXT,
            name TEXT,
            tariff TEXT,
            status TEXT DEFAULT 'inactive'
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS receipts (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            username TEXT,
            selected_tariff TEXT,
            receipt_photo TEXT,
            status TEXT DEFAULT 'pending',
            FOREIGN KEY (user_id) REFERENCES users(tg_id)
        )
    ''')
    conn.commit()
    conn.close()

def check_user_exists(tg_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE tg_id = ?", (tg_id,))
    user = cursor.fetchone()
    conn.close()
    return user

def add_user(tg_id, username, name, password):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (tg_id, username, name, password) VALUES (?, ?, ?, ?)",
                   (tg_id, username, name, password))
    conn.commit()
    conn.close()

def get_all_users():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT tg_id, username, name, tariff FROM users")
    users = cursor.fetchall()
    conn.close()
    return users

def get_user_receipts(receipt_id=None):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    if receipt_id:
        cursor.execute("SELECT id, user_id, username, selected_tariff, receipt_photo FROM receipts WHERE id = ?", (receipt_id,))
        receipt = cursor.fetchone()
        conn.close()
        return receipt
    else:
        cursor.execute("SELECT id, user_id, username, selected_tariff, receipt_photo FROM receipts WHERE status='pending'")
        receipts = cursor.fetchall()
        conn.close()
        return receipts

def add_receipt(user_id, username, selected_tariff, receipt_photo):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO receipts (user_id, username, selected_tariff, receipt_photo) VALUES (?, ?, ?, ?)",
                   (user_id, username, selected_tariff, receipt_photo))
    conn.commit()
    conn.close()

def update_receipt_status(receipt_id, status):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE receipts SET status = ? WHERE id = ?", (status, receipt_id))
    conn.commit()
    conn.close()

def update_user_status(user_id, status):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET status = ? WHERE tg_id = ?", (status, user_id))
    conn.commit()
    conn.close()

def update_user_tariff(user_id, tariff):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET tariff = ? WHERE tg_id = ?", (tariff, user_id))
    conn.commit()
    conn.close()

def delete_receipt(receipt_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM receipts WHERE id = ?", (receipt_id,))
    conn.commit()
    conn.close()


init_db()
