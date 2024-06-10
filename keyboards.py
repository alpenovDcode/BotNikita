from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton

def tariff_buttons():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton('🌟 Тариф Старт 🌟'))
    keyboard.add(KeyboardButton('🚀 Тариф Развитие 🚀'))
    keyboard.add(KeyboardButton('💼 Тариф Профессионал 💼'))
    return keyboard

def payment_button():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton('💳 Оплатить', callback_data='pay'))
    return keyboard

def admin_menu_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton('👥 Список пользователей'))
    keyboard.add(KeyboardButton('📜 Чеки пользователей'))
    keyboard.add(KeyboardButton('❓ Ответы на вопросы'))
    keyboard.add(KeyboardButton('➕ Добавить шпаргалку'))
    keyboard.add(KeyboardButton('✏️ Редактировать шпаргалку'))
    keyboard.add(KeyboardButton('🔍 Просмотр шпаргалок'))
    keyboard.add(KeyboardButton('📧 Рассылка'))
    keyboard.add(KeyboardButton('➕ Добавить администратора'))
    return keyboard

def receipt_action_buttons(receipt_id, selected_tariff):
    buttons = [
        InlineKeyboardButton(text="✅ Подтвердить", callback_data=f"approve_{receipt_id}"),
        InlineKeyboardButton(text="❌ Отклонить", callback_data=f"reject_{receipt_id}")
    ]
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(*buttons)
    return keyboard

def user_profile_update_buttons(tariff):
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(InlineKeyboardButton('✏️ Редактировать имя', callback_data='edit_name'))
    keyboard.add(InlineKeyboardButton('📞 Редактировать контактные данные', callback_data='edit_contact'))
    return keyboard

def user_profile_buttons(tariff):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton('📞 Связаться с менеджером'))
    if tariff != "Тариф Профессионал":
        keyboard.add(KeyboardButton('🔄 Перейти на новый тариф'))
    keyboard.add(KeyboardButton('🔙 Назад'))
    return keyboard

def start_buttons():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton('👤 Мой профиль'))
    keyboard.row(KeyboardButton('💬 ChatGPT'), KeyboardButton('📚 Полезные материалы'))
    keyboard.add(KeyboardButton('📞 Связаться с менеджером'))
    return keyboard

def development_buttons():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton('👤 Мой профиль'))
    keyboard.row(KeyboardButton('💬 ChatGPT'), KeyboardButton('📚 Полезные материалы'))
    keyboard.add(KeyboardButton('🔍 Проверка этапов'))
    keyboard.add(KeyboardButton('📞 Связаться с менеджером'))
    return keyboard

def professional_buttons():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton('👤 Мой профиль'))
    keyboard.row(KeyboardButton('💬 ChatGPT'), KeyboardButton('📚 Полезные материалы'))
    keyboard.add(KeyboardButton('📞 Связаться с менеджером'))
    return keyboard

def upgrade_buttons():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton('🚀 Тариф Развитие', callback_data='upgrade_development'))
    keyboard.add(InlineKeyboardButton('💼 Тариф Профессионал', callback_data='upgrade_professional'))
    return keyboard

def back_button():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton('🔙 Назад'))
    return keyboard
