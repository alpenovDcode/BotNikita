import logging
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import state
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from DB import delete_receipt, check_user_exists, add_user, get_all_users, get_user_receipts, add_receipt, update_receipt_status, update_user_status, update_user_tariff
from keyboards import start_buttons, tariff_buttons, payment_button, admin_menu_keyboard, receipt_action_buttons, user_profile_buttons, start_buttons, development_buttons, professional_buttons, upgrade_buttons
from states import RegisterState, PaymentState, StartTariffState, UpgradeTariffState
from mainBot import dp, bot

from config import ADMINS

logger = logging.getLogger(__name__)

async def delete_previous_message(message: types.Message):
    try:
        await bot.delete_message(message.chat.id, message.message_id)
    except Exception as e:
        logger.error(f"Error deleting message: {e}")

# Обработчик команды /start
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    try:
        user_id = message.from_user.id
        await delete_previous_message(message)

        if user_id in ADMINS:
            await bot.send_message(user_id, "Добро пожаловать, Администратор!", reply_markup=admin_menu_keyboard())
            return

        user = check_user_exists(user_id)
        if user:
            # Пользователь найден в базе данных, проверяем его тариф
            tariff = user[5]
            if tariff == "Тариф Старт":
                await bot.send_message(user_id, "Добро пожаловать! Ваш текущий тариф - 'Старт'.", reply_markup=start_buttons())
                await StartTariffState.in_start_menu.set()
            elif tariff == "Тариф Развитие":
                await bot.send_message(user_id, "Добро пожаловать! Ваш текущий тариф - 'Развитие'.", reply_markup=development_buttons())
                await StartTariffState.in_start_menu.set()
            elif tariff == "Тариф Профессионал":
                await bot.send_message(user_id, "Добро пожаловать! Ваш текущий тариф - 'Профессионал'.", reply_markup=professional_buttons())
                await StartTariffState.in_start_menu.set()
            else:
                await bot.send_message(user_id, "Ваш тариф не найден. Пожалуйста, выберите тариф:", reply_markup=tariff_buttons())
        else:
            # Пользователь не найден в базе данных, предлагаем регистрацию
            await bot.send_message(user_id, "Добро пожаловать! Давайте зарегистрируем вас. Введите ваше имя:")
            await RegisterState.waiting_for_name.set()
    except Exception as e:
        logger.exception("Ошибка при обработке команды /start: %s", e)


# Обработчик регистрации имени
@dp.message_handler(state=RegisterState.waiting_for_name)
async def process_name(message: types.Message, state: FSMContext):
    try:
        await state.update_data(name=message.text)
        await delete_previous_message(message)
        await bot.send_message(message.from_user.id, "Теперь придумайте и введите ваш пароль:")
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

        add_user(tg_id, f"@{username}", name, password)
        await delete_previous_message(message)
        await bot.send_message(tg_id, "Регистрация завершена! Выберите тариф:", reply_markup=tariff_buttons())
        await state.finish()
    except Exception as e:
        logger.exception("Ошибка при регистрации пароля: %s", e)


# Обработчик для кнопок тарифов
@dp.message_handler(lambda message: message.text in ["Тариф Старт", "Тариф Развитие", "Тариф Профессионал"])
async def show_tariff_details(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user = check_user_exists(user_id)
    await delete_previous_message(message)

    if not user:
        await bot.send_message(user_id, "Пожалуйста, зарегистрируйтесь, используя команду /start.")
        return

    await state.update_data(selected_tariff=message.text)
    tariffs_info = {
        "Тариф Старт": "Тариф \"Старт\"\n- Доступ к базовым функциям чат-бота на базе ChatGPT.\n- Шпаргалка с описанием семи ключевых этапов для развития бизнеса от идеи до первых продаж.",
        "Тариф Развитие": "Тариф \"Развитие\"\n- Всё, что включает тариф \"Старт\".\n- Возможность выбора одного из бизнес-этапов для профессиональной проверки консультантом.\n- Клиентский менеджер связывается с клиентом для уточнения деталей и передачи информации консультанту. Ответы возвращаются через чат-бот.",
        "Тариф Профессионал": "Тариф \"Профессионал\"\n- Всё, что доступно в тарифе \"Старт\".\n- Возможность глубокой валидации одного из этапов бизнеса в личном общении с консультантом.\n- Клиентский менеджер организует встречу между клиентом и консультантом для более тесного обсуждения и решения вопросов."
    }

    tariff_text = tariffs_info.get(message.text, "Информация о тарифе не найдена.")
    await bot.send_message(user_id, tariff_text, reply_markup=payment_button())

# Обработчик для кнопки "Оплатить"
@dp.callback_query_handler(lambda c: c.data == 'pay', state='*')
async def process_payment(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, "Пожалуйста, прикрепите скриншот чека об оплате.")
    await PaymentState.waiting_for_receipt.set()

# Обработчик для получения скриншота чека
@dp.message_handler(content_types=types.ContentType.PHOTO, state=PaymentState.waiting_for_receipt)
async def handle_receipt(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    selected_tariff = user_data.get('selected_tariff')
    receipt_photo = message.photo[-1].file_id
    tg_id = message.from_user.id
    username = message.from_user.username

    add_receipt(tg_id, username, selected_tariff, receipt_photo)
    await delete_previous_message(message)
    await bot.send_message(tg_id, "Ваш чек отправлен на проверку. Ожидайте подтверждения.")
    await state.finish()

# Обработчик для перехода на новый тариф
@dp.message_handler(lambda message: message.text == "Перейти на новый тариф", state=StartTariffState.in_profile_menu)
async def upgrade_tariff_menu(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user = check_user_exists(user_id)
    await delete_previous_message(message)

    if user[5] == "Тариф Старт":
        keyboard = upgrade_buttons()
        await bot.send_message(user_id, "Выберите новый тариф:", reply_markup=keyboard)
        await UpgradeTariffState.waiting_for_new_tariff.set()
    elif user[5] == "Тариф Развитие":
        await state.update_data(selected_tariff="Тариф Профессионал")
        await bot.send_message(user_id, "Перейти на тариф 'Профессионал'. Пожалуйста, прикрепите скриншот чека об оплате.", reply_markup=payment_button())
        await PaymentState.waiting_for_receipt.set()

# Обработчик для выбора нового тарифа
@dp.callback_query_handler(lambda c: c.data in ["upgrade_development", "upgrade_professional"], state=UpgradeTariffState.waiting_for_new_tariff)
async def process_upgrade_tariff(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    new_tariff = "Тариф Развитие" if callback_query.data == "upgrade_development" else "Тариф Профессионал"
    await state.update_data(selected_tariff=new_tariff)
    await bot.send_message(callback_query.from_user.id, f"Перейти на тариф '{new_tariff}'. Пожалуйста, прикрепите скриншот чека об оплате.", reply_markup=payment_button())
    await PaymentState.waiting_for_receipt.set()
    logger.info(f"User {callback_query.from_user.id} selected tariff: {new_tariff}")

# Обработчик для кнопки "Список пользователей"
@dp.message_handler(lambda message: message.text == "Список пользователей")
async def list_users(message: types.Message):
    user_id = message.from_user.id
    if user_id not in ADMINS:
        await bot.send_message(user_id, "У вас нет доступа к этой команде.")
        await delete_previous_message(message)
        return

    users = get_all_users()
    users_text = "\n".join([f"{user[1]}: {user[2]}" for user in users])
    await bot.send_message(user_id, f"Список пользователей:\n{users_text}")
    await delete_previous_message(message)

# Обработчик для кнопки "Чеки пользователей"
@dp.message_handler(lambda message: message.text == "Чеки пользователей")
async def list_receipts(message: types.Message):
    user_id = message.from_user.id
    if user_id not in ADMINS:
        await bot.send_message(user_id, "У вас нет доступа к этой команде.")
        await delete_previous_message(message)
        return

    receipts = get_user_receipts()
    for receipt in receipts:
        caption = f"@{receipt[2]}\n{receipt[3]}"
        await bot.send_message(receipt[1], caption=caption, reply_markup=receipt_action_buttons(receipt[0], receipt[3]))
    await delete_previous_message(message)

# Обработчик для профиля пользователя
@dp.message_handler(lambda message: message.text == "Мой профиль")
async def user_profile(message: types.Message):
    user_id = message.from_user.id
    user = check_user_exists(user_id)
    await delete_previous_message(message)

    if not user:
        await bot.send_message(user_id, "Пожалуйста, зарегистрируйтесь, используя команду /start.")
        return

    profile_info = f"Имя: {user[4]}\nТариф: {user[5]}\nКонтактные данные: @{user[2]}"
    await bot.send_message(user_id, profile_info, reply_markup=user_profile_buttons(user[5]))

# Обработчик для кнопки "Связаться с менеджером"
@dp.message_handler(lambda message: message.text == "Связаться с менеджером")
async def contact_manager(message: types.Message):
    await delete_previous_message(message)
    await bot.send_message(message.from_user.id, "Введите ваш вопрос. В ближайшее время с вами свяжутся.")
    await PaymentState.waiting_for_question.set()

# Обработчик для получения вопроса пользователя менеджеру
@dp.message_handler(state=PaymentState.waiting_for_question)
async def handle_question(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    username = message.from_user.username
    question = message.text

    for admin_id in ADMINS:
        await bot.send_message(admin_id, f"Пользователь @{username} задал вопрос: {question}")

    await delete_previous_message(message)
    await bot.send_message(user_id, "Ваш вопрос отправлен. В ближайшее время с вами свяжутся.")
    await state.finish()

# Handler for approval and rejection of receipts
@dp.callback_query_handler(lambda c: c.data.startswith('approve_') or c.data.startswith('reject_'))
async def handle_receipt_action(callback_query: types.CallbackQuery):
    action, receipt_id = callback_query.data.split('_')
    receipt = get_user_receipts(receipt_id)

    if not receipt:
        await bot.answer_callback_query(callback_query.id, text="Чек не найден", show_alert=True)
        return

    user_id = receipt[1]
    selected_tariff = receipt[3]

    if action == 'approve':
        update_receipt_status(receipt_id, 'approved')
        update_user_status(user_id, 'active')
        update_user_tariff(user_id, selected_tariff)
        delete_receipt(receipt_id)
        await bot.send_message(callback_query.from_user.id, f"Чек {receipt_id} подтверждён.")
        try:
            await bot.send_message(user_id, "Ваш чек был подтверждён. Ваша покупка завершена успешно!")
            # Обновляем кнопки в зависимости от нового тарифа
            if selected_tariff == "Тариф Старт":
                await bot.send_message(user_id, "Доступ к вашим функциям:", reply_markup=start_buttons())
            elif selected_tariff == "Тариф Развитие":
                await bot.send_message(user_id, "Доступ к вашим функциям:", reply_markup=development_buttons())
            elif selected_tariff == "Тариф Профессионал":
                await bot.send_message(user_id, "Доступ к вашим функциям:", reply_markup=professional_buttons())
        except Exception as e:
            logger.error(f"Error sending message to user {user_id}: {e}")

    elif action == 'reject':
        update_receipt_status(receipt_id, 'rejected')
        await bot.send_message(callback_query.from_user.id, f"Чек {receipt_id} отклонён.")


# Обработчик для кнопок тарифа "Старт"
@dp.message_handler(lambda message: message.text == "Тариф Старт")
async def start_tariff_menu(message: types.Message, state: FSMContext):
    keyboard = start_buttons()
    await delete_previous_message(message)
    await bot.send_message(message.from_user.id, "Меню тарифа 'Старт':", reply_markup=keyboard)
    await StartTariffState.in_start_menu.set()

# Обработчик для профиля пользователя
@dp.message_handler(lambda message: message.text == "Мой профиль", state=[StartTariffState.in_start_menu, StartTariffState.in_profile_menu])
async def user_profile(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user = check_user_exists(user_id)
    await delete_previous_message(message)

    if not user:
        await bot.send_message(user_id, "Пожалуйста, зарегистрируйтесь, используя команду /start.")
        return

    profile_info = f"Имя: {user[4]}\nТариф: {user[5]}\nКонтактные данные: @{user[2]}"
    keyboard = user_profile_buttons(user[5])
    await bot.send_message(user_id, profile_info, reply_markup=keyboard)
    await StartTariffState.in_profile_menu.set()

@dp.message_handler(lambda message: message.text == "ChatGPT", state=StartTariffState.in_start_menu)
async def chatgpt(message: types.Message):
    await delete_previous_message(message)
    await bot.send_message(message.from_user.id, "Добро пожаловать в ChatGPT! Какой у вас вопрос?")

@dp.message_handler(lambda message: message.text == "Полезные материалы", state=StartTariffState.in_start_menu)
async def useful_materials(message: types.Message):
    await delete_previous_message(message)
    await bot.send_message(message.from_user.id, "Вот полезные материалы для вас:\n1. Материал 1\n2. Материал 2")

@dp.message_handler(lambda message: message.text == "Связаться с менеджером", state=StartTariffState.in_start_menu)
async def contact_manager(message: types.Message):
    await delete_previous_message(message)
    await bot.send_message(message.from_user.id, "Введите ваш вопрос. В ближайшее время с вами свяжутся.")
    await PaymentState.waiting_for_question.set()

@dp.message_handler(lambda message: message.text == "Назад", state=StartTariffState.in_profile_menu)
async def back_to_start_menu_from_profile(message: types.Message, state: FSMContext):
    keyboard = start_buttons()
    await delete_previous_message(message)
    await bot.send_message(message.from_user.id, "Главный экран:", reply_markup=keyboard)
    await StartTariffState.in_start_menu.set()
