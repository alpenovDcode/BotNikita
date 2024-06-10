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
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            username TEXT,
            question TEXT
        )
    ''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS cheat_sheets (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            content TEXT NOT NULL
        )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS cheat_sheet_files (
            id INTEGER PRIMARY KEY,
            cheat_sheet_id INTEGER NOT NULL,
            file_id TEXT NOT NULL,
            file_type TEXT NOT NULL,
            FOREIGN KEY (cheat_sheet_id) REFERENCES cheat_sheets(id)
        )''')
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
        cursor.execute("SELECT id, user_id, username, selected_tariff, receipt_photo, status FROM receipts WHERE id = ?", (receipt_id,))
        receipt = cursor.fetchone()
        conn.close()
        return receipt
    else:
        cursor.execute("SELECT id, user_id, username, selected_tariff, receipt_photo, status FROM receipts WHERE status='pending'")
        receipts = cursor.fetchall()
        print("Fetched receipts:", receipts)  # Добавим этот вывод для отладки
        conn.close()
        return receipts



def add_receipt(user_id, username, selected_tariff, receipt_photo, status='pending'):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO receipts (user_id, username, selected_tariff, receipt_photo, status) VALUES (?, ?, ?, ?, ?)",
                   (user_id, username, selected_tariff, receipt_photo, status))
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


def save_question(user_id, username, question):
    conn = sqlite3.connect('database.db')  # Замените 'database.db' на ваш путь к базе данных
    cursor = conn.cursor()

    cursor.execute("INSERT INTO questions (user_id, username, question) VALUES (?, ?, ?)",
                   (user_id, username, question))
    conn.commit()
    conn.close()


def get_all_questions():
    conn = sqlite3.connect('database.db')  # Замените 'database.db' на ваш путь к базе данных
    cursor = conn.cursor()

    cursor.execute("SELECT id, user_id, question FROM questions")
    questions = cursor.fetchall()
    conn.close()
    return questions

def delete_question(question_id):
    conn = sqlite3.connect('database.db')  # Замените 'database.db' на ваш путь к базе данных
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM questions WHERE id = ?", (question_id,))
        conn.commit()
    except Exception as e:
        print(f"Error deleting question: {e}")
    finally:
        conn.close()

def update_user_name(user_id, new_name):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET name = ? WHERE tg_id = ?", (new_name, user_id))
    conn.commit()
    conn.close()

def update_user_contact(user_id, new_contact):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET username = ? WHERE tg_id = ?", (new_contact, user_id))
    conn.commit()
    conn.close()

def save_cheat_sheet(title, content):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO cheat_sheets (title, content) VALUES (?, ?)", (title, content))
    cheat_sheet_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return cheat_sheet_id

def save_cheat_sheet_file(cheat_sheet_id, file_id, file_type):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO cheat_sheet_files (cheat_sheet_id, file_id, file_type) VALUES (?, ?, ?)", (cheat_sheet_id, file_id, file_type))
    conn.commit()
    conn.close()

def get_cheat_sheets():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, content FROM cheat_sheets")
    rows = cursor.fetchall()
    cheat_sheets = [{"id": row[0], "title": row[1], "content": row[2]} for row in rows]
    for cheat_sheet in cheat_sheets:
        cursor.execute("SELECT id, file_id, file_type FROM cheat_sheet_files WHERE cheat_sheet_id=?", (cheat_sheet["id"],))
        files = cursor.fetchall()
        cheat_sheet["files"] = [{"id": file[0], "file_id": file[1], "file_type": file[2]} for file in files]
    conn.close()
    return cheat_sheets

def update_cheat_sheet(cheat_sheet_id, title, content):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE cheat_sheets SET title=?, content=? WHERE id=?", (title, content, cheat_sheet_id))
    conn.commit()
    conn.close()

def delete_cheat_sheet(cheat_sheet_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM cheat_sheets WHERE id=?", (cheat_sheet_id,))
    cursor.execute("DELETE FROM cheat_sheet_files WHERE cheat_sheet_id=?", (cheat_sheet_id,))
    conn.commit()
    conn.close()

def delete_cheat_sheet_file(file_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM cheat_sheet_files WHERE id=?", (file_id,))
    conn.commit()
    conn.close()

def get_cheat_sheet_by_id(cheat_sheet_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, content FROM cheat_sheets WHERE id=?", (cheat_sheet_id,))
    row = cursor.fetchone()
    cheat_sheet = {"id": row[0], "title": row[1], "content": row[2]} if row else None
    if cheat_sheet:
        cursor.execute("SELECT id, file_id, file_type FROM cheat_sheet_files WHERE cheat_sheet_id=?", (cheat_sheet_id,))
        files = cursor.fetchall()
        cheat_sheet["files"] = [{"id": file[0], "file_id": file[1], "file_type": file[2]} for file in files]
    conn.close()
    return cheat_sheet

init_db()
