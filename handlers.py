import logging
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from DB import check_user_exists, check_credentials, add_user
from keyboards import main_menu_keyboard
from states import AuthState, RegisterState
from mainBot import dp

logger = logging.getLogger(__name__)


# Обработчик команды /start
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    try:
        user_id = message.from_user.id
        username = message.from_user.username

        user = check_user_exists(user_id)

        if user:
            await message.reply("Привет! Пожалуйста, введите ваш логин:")
            await AuthState.waiting_for_username.set()
        else:
            await message.reply("Добро пожаловать! Давайте зарегистрируем вас. Введите ваше имя:")
            await RegisterState.waiting_for_name.set()
    except Exception as e:
        logger.exception("Ошибка при обработке команды /start: %s", e)

# Обработчик регистрации имени
@dp.message_handler(state=RegisterState.waiting_for_name)
async def process_name(message: types.Message, state: FSMContext):
    try:
        await state.update_data(name=message.text)
        await message.reply("Теперь придумайте и введите ваш пароль:")
        await RegisterState.waiting_for_password.set()
    except Exception as e:
        logger.exception("Ошибка при регистрации имени: %s", e)

# Обработчик регистрации пароля
@dp.message_handler(state=RegisterState.waiting_for_password)
async def process_password_register(message: types.Message, state: FSMContext):
    try:
        user_data = await state.get_data()
        name = user_data['name']
        password = message.text
        tg_id = message.from_user.id
        username = message.from_user.username

        add_user(tg_id, username, name, password)
        await message.reply("Регистрация завершена! Теперь вы можете авторизоваться. Введите ваш логин:")
        await AuthState.waiting_for_username.set()
    except Exception as e:
        logger.exception("Ошибка при регистрации пароля: %s", e)

# Обработчик получения логина
@dp.message_handler(state=AuthState.waiting_for_username)
async def process_username(message: types.Message, state: FSMContext):
    try:
        await state.update_data(username=message.text)
        await message.reply("Теперь введите ваш пароль:")
        await AuthState.waiting_for_password.set()
    except Exception as e:
        logger.exception("Ошибка при обработке логина: %s", e)

# Обработчик получения пароля
@dp.message_handler(state=AuthState.waiting_for_password)
async def process_password_auth(message: types.Message, state: FSMContext):
    try:
        user_data = await state.get_data()
        username = user_data['username']
        password = message.text

        user = check_credentials(username, password)
        if user:
            await message.reply(f"Добро пожаловать, {user[3]}!", reply_markup=main_menu_keyboard())
            await state.finish()
        else:
            await message.reply("Неверный логин или пароль. Попробуйте снова. Введите ваш логин:")
            await AuthState.waiting_for_username.set()
    except Exception as e:
        logger.exception("Ошибка при обработке пароля: %s", e)
