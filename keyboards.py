from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton

def tariff_buttons():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton('Тариф Старт'))
    keyboard.add(KeyboardButton('Тариф Развитие'))
    keyboard.add(KeyboardButton('Тариф Профессионал'))
    return keyboard

def payment_button():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton('Оплатить', callback_data='pay'))
    return keyboard

def admin_menu_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton('Список пользователей'))
    keyboard.add(KeyboardButton('Чеки пользователей'))
    return keyboard

def receipt_action_buttons(receipt_id, selected_tariff):
    buttons = [
        InlineKeyboardButton(text="Approve", callback_data=f"approve_{receipt_id}"),
        InlineKeyboardButton(text="Reject", callback_data=f"reject_{receipt_id}")
    ]
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(*buttons)
    return keyboard

def user_profile_buttons():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton('Связаться с менеджером'))
    keyboard.add(KeyboardButton('Перейти на новый тариф'))
    return keyboard

def start_buttons():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton('Шпаргалка'))
    keyboard.add(KeyboardButton('Связаться с менеджером'))
    return keyboard

def development_buttons():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton('Шпаргалка'))
    keyboard.add(KeyboardButton('Связаться с менеджером'))
    keyboard.add(KeyboardButton('Проверка этапов'))
    return keyboard

def professional_buttons():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton('Шпаргалка'))
    keyboard.add(KeyboardButton('Связаться с менеджером'))
    keyboard.add(KeyboardButton('Глубокая валидация'))
    return keyboard

def start_buttons():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton('Мой профиль'))
    keyboard.add(KeyboardButton('ChatGPT'))
    keyboard.add(KeyboardButton('Полезные материалы'))
    keyboard.add(KeyboardButton('Связаться с менеджером'))
    return keyboard

def profile_buttons():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton('Назад'))
    return keyboard
