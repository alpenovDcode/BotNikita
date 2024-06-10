import logging

import openai
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import state
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from DB import delete_receipt, check_user_exists, add_user, get_all_users, get_user_receipts, add_receipt, \
    update_receipt_status, update_user_status, update_user_tariff, get_all_questions, save_question, delete_question, \
    update_user_name, update_user_contact, save_cheat_sheet, get_cheat_sheets, save_cheat_sheet_file, \
    update_cheat_sheet, delete_cheat_sheet_file, delete_cheat_sheet, get_cheat_sheet_by_id
from keyboards import start_buttons, tariff_buttons, payment_button, admin_menu_keyboard, receipt_action_buttons, \
    user_profile_buttons, start_buttons, development_buttons, professional_buttons, upgrade_buttons, back_button, user_profile_update_buttons
from states import RegisterState, PaymentState, StartTariffState, UpgradeTariffState, BroadcastState, AnswerState, \
    EditProfileState, CheatSheetState, AddAdminState
from mainBot import dp, bot

from config import ADMINS, generate_response

logger = logging.getLogger(__name__)

questions = [
    "Кто ваши основные клиенты?",
    "Какую ценность вы предоставляете своим клиентам?",
    "Как вы привлекаете своих клиентов?",
    "Какого типа взаимоотношения вы устанавливаете с каждым клиентским сегментом?",
    "Как вы зарабатываете на каждом клиентском сегменте?",
    "Какие ключевые ресурсы необходимы для реализации вашего ценностного предложения?",
    "Какие основные виды деятельности необходимы для реализации вашего ценностного предложения?",
    "С кем вы сотрудничаете для достижения своих целей?",
    "Какие основные затраты связаны с вашим бизнесом?"
]

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
            await bot.send_message(user_id, "👋 Добро пожаловать, Администратор!", reply_markup=admin_menu_keyboard())
            return

        user = check_user_exists(user_id)
        if user:
            # Пользователь найден в базе данных, проверяем его тариф
            tariff = user[5]
            if tariff == "🌟 Тариф Старт 🌟":
                await bot.send_message(user_id, "👋 Добро пожаловать! Ваш текущий тариф - 🌟 'Старт'.", reply_markup=start_buttons())
                await StartTariffState.in_start_menu.set()
            elif tariff == "🚀 Тариф Развитие 🚀":
                await bot.send_message(user_id, "👋 Добро пожаловать! Ваш текущий тариф - 🚀 'Развитие'.", reply_markup=development_buttons())
                await StartTariffState.in_start_menu.set()
            elif tariff == "💼 Тариф Профессионал 💼":
                await bot.send_message(user_id, "👋 Добро пожаловать! Ваш текущий тариф - 💼 'Профессионал'.", reply_markup=professional_buttons())
                await StartTariffState.in_start_menu.set()
            else:
                await bot.send_message(user_id, "❗ Ваш тариф не найден. Пожалуйста, выберите тариф:", reply_markup=tariff_buttons())
        else:
            # Пользователь не найден в базе данных, предлагаем регистрацию
            await bot.send_message(user_id, "👋 Добро пожаловать! Давайте зарегистрируем вас. Введите ваше имя:")
            await RegisterState.waiting_for_name.set()
    except Exception as e:
        logger.exception("Ошибка при обработке команды /start: %s", e)



# Обработчик регистрации имени
@dp.message_handler(state=RegisterState.waiting_for_name)
async def process_name(message: types.Message, state: FSMContext):
    try:
        await state.update_data(name=message.text)
        await delete_previous_message(message)
        await bot.send_message(message.from_user.id, "✏️ Теперь придумайте и введите ваш пароль:")
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
        await bot.send_message(tg_id, "✅ Регистрация завершена! Выберите тариф:", reply_markup=tariff_buttons())
        await state.finish()
    except Exception as e:
        logger.exception("Ошибка при регистрации пароля: %s", e)


# Обработчик для кнопок тарифов
@dp.message_handler(lambda message: message.text in ["🌟 Тариф Старт 🌟", "🚀 Тариф Развитие 🚀", "💼 Тариф Профессионал 💼"])
async def show_tariff_details(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user = check_user_exists(user_id)
    await delete_previous_message(message)

    if not user:
        await bot.send_message(user_id, "❗ Пожалуйста, зарегистрируйтесь, используя команду /start.")
        return

    await state.update_data(selected_tariff=message.text)
    tariffs_info = {
        "🌟 Тариф Старт 🌟": (
            "🌟 Тариф \"Старт\"\n"
            "Заложите основу вашего успеха\n\n"
            "✔ **Полный стартовый набор**\n"
            "Получите все необходимые шаблоны для начала бизнеса, включая бизнес-план и финансовую модель.\n\n"
            "✔ **Шаблоны**\n"
            "✔ **Интеллектуальное руководство**\n"
            "Воспользуйтесь нашими ИИ для анализа и улучшения вашего плана на каждом шагу.\n\n"
            "Эффективный старт за минимальные вложения. Начните сейчас и сделайте первый шаг к своему бизнесу!\n\n"
            "**Цена: 999Р**"
        ),
        "🚀 Тариф Развитие 🚀": (
            "🚀 Тариф \"Развитие\"\n"
            "Уверенность на каждом шагу\n\n"
            "✔ **Расширенные возможности**\n"
            "Все преимущества тарифа \"Старт\" плюс индивидуальный подход к вашим потребностям.\n\n"
            "✔ **Персональная валидация**\n"
            "Наши эксперты при помощи искусственного интеллекта помогут реализовать ваш проект на любом из его этапов.\n\n"
            "✔ **Этапы**\n\n"
            "Преодолейте страх и сделайте следующий шаг к успеху с \"Развитием\"!\n\n"
            "**Цена: 4999Р**"
        ),
        "💼 Тариф Профессионал 💼": (
            "💼 Тариф \"Профессионал\"\n"
            "Персональный подход к вашему успеху\n\n"
            "✔ **Все преимущества тарифов \"Старт\" и \"Развитие\" плюс исключительное общение с ведущими экспертами в вашей отрасли.**\n\n"
            "✔ **Личные консультации и наставничество**\n"
            "С возможностью глубокого анализа и корректировки вашего бизнес-плана.\n\n"
            "✔ **Возможность стратегического партнерства, включая поддержку в принятии ключевых решений.**\n\n"
            "**Цена: 49999Р**"
        )
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
    await bot.send_message(tg_id, "Ваш чек отправлен на проверку. Ожидайте подтверждения.", reply_markup=start_buttons())
    await state.finish()


# Обработчик для перехода на новый тариф
@dp.message_handler(lambda message: message.text == "Перейти на новый тариф", state=StartTariffState.in_profile_menu)
async def upgrade_tariff_menu(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user = check_user_exists(user_id)
    await delete_previous_message(message)

    if user[5] == "🌟 Тариф Старт 🌟":
        keyboard = upgrade_buttons()
        await bot.send_message(user_id, "Выберите новый тариф:", reply_markup=keyboard)
        await UpgradeTariffState.waiting_for_new_tariff.set()
    elif user[5] == "🚀 Тариф Развитие 🚀":
        await state.update_data(selected_tariff="💼 Тариф Профессионал 💼")
        await bot.send_message(user_id, "Перейти на тариф 'Профессионал'. Пожалуйста, прикрепите скриншот чека об оплате.", reply_markup=payment_button())
        await UpgradeTariffState.in_payment.set()


# Обработчик для выбора нового тарифа
@dp.callback_query_handler(lambda c: c.data in ["upgrade_development", "upgrade_professional"], state=UpgradeTariffState.waiting_for_new_tariff)
async def process_upgrade_tariff(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    new_tariff = "🚀 Тариф Развитие 🚀" if callback_query.data == "upgrade_development" else "💼 Тариф Профессионал 💼"
    await state.update_data(selected_tariff=new_tariff)
    await bot.send_message(callback_query.from_user.id, f"Перейти на тариф '{new_tariff}'. Пожалуйста, прикрепите скриншот чека об оплате.", reply_markup=payment_button())
    await PaymentState.waiting_for_receipt.set()
    logger.info(f"User {callback_query.from_user.id} selected tariff: {new_tariff}")

# Обработчик для кнопки "Список пользователей"
@dp.message_handler(lambda message: message.text == "👥 Список пользователей")
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
@dp.message_handler(lambda message: message.text == "📜 Чеки пользователей")
async def list_receipts(message: types.Message):
    user_id = message.from_user.id
    if user_id not in ADMINS:
        await bot.send_message(user_id, "У вас нет доступа к этой команде.")
        await delete_previous_message(message)
        return

    receipts = get_user_receipts()
    for receipt in receipts:
        caption = f"@{receipt[2]}\n{receipt[3]}"
        receipt_photo = receipt[4]  # Получаем ID фотографии
        await bot.send_photo(user_id, photo=receipt_photo, caption=caption, reply_markup=receipt_action_buttons(receipt[0], receipt[3]))
    await delete_previous_message(message)

@dp.message_handler(lambda message: message.text == "Мой профиль",
                    state=[StartTariffState.in_start_menu, StartTariffState.in_profile_menu])
async def user_profile(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    logger.info(f"Handling 'Мой профиль' for user {user_id}")

    user = check_user_exists(user_id)
    if not user:
        logger.info(f"User {user_id} not found in the database.")
        await delete_previous_message(message)
        await bot.send_message(user_id, "Пожалуйста, зарегистрируйтесь, используя команду /start.")
        return

    await delete_previous_message(message)
    logger.info(f"User {user_id} found: {user}")

    profile_info = f"Имя: {user[4]}\nТариф: {user[5]}\nКонтактные данные: {user[2]}"
    keyboard = user_profile_update_buttons(user[5])
    await bot.send_message(user_id, profile_info, reply_markup=keyboard)
    await StartTariffState.in_profile_menu.set()


# Обработчик для inline кнопок редактирования
@dp.callback_query_handler(lambda c: c.data == 'edit_name', state=StartTariffState.in_profile_menu)
async def edit_name(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.send_message(callback_query.from_user.id, "Введите новое имя:")
    await EditProfileState.waiting_for_new_name.set()

@dp.callback_query_handler(lambda c: c.data == 'edit_contact', state=StartTariffState.in_profile_menu)
async def edit_contact(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.send_message(callback_query.from_user.id, "Введите новые контактные данные:")
    await EditProfileState.waiting_for_new_contact.set()

# Обработчики для получения новых значений и обновления базы данных
@dp.message_handler(state=EditProfileState.waiting_for_new_name)
async def process_new_name(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    new_name = message.text
    update_user_name(user_id, new_name)
    await bot.send_message(user_id, f"Ваше имя обновлено на {new_name}.")
    await state.finish()
    await user_profile(message, state)

@dp.message_handler(state=EditProfileState.waiting_for_new_contact)
async def process_new_contact(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    new_contact = message.text
    update_user_contact(user_id, new_contact)
    await bot.send_message(user_id, f"Ваши контактные данные обновлены на {new_contact}.")
    await state.finish()
    await user_profile(message, state)


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

    save_question(user_id, f"@{username}", question)  # Сохраняем вопрос в базу данных

    await delete_previous_message(message)
    await bot.send_message(user_id, "Ваш вопрос отправлен. В ближайшее время с вами свяжутся.", reply_markup=start_buttons())
    await state.finish()


@dp.message_handler(lambda message: message.text == "❓ Ответы на вопросы")
async def list_questions(message: types.Message):
    user_id = message.from_user.id
    if user_id not in ADMINS:
        await bot.send_message(chat_id=user_id, text="У вас нет доступа к этой команде.")
        await delete_previous_message(message)
        return

    questions = get_all_questions()
    if questions:
        for question in questions:
            question_text = f"Пользователь {question[1]} задал вопрос: {question[2]}"
            keyboard = InlineKeyboardMarkup().add(
                InlineKeyboardButton("Ответить", callback_data=f"answer_{question[0]}_{question[1]}"))
            await bot.send_message(chat_id=user_id, text=question_text, reply_markup=keyboard)
    else:
        await bot.send_message(chat_id=user_id, text="Нет новых вопросов.")
    await delete_previous_message(message)

@dp.callback_query_handler(lambda c: c.data.startswith('answer_'))
async def handle_answer_button(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    data = callback_query.data.split('_')
    question_id = data[1]
    user_id = data[2]

    await state.update_data(current_user_id=user_id, question_id=question_id)
    reply_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    reply_markup.add(types.KeyboardButton('Завершить ответ'))
    await bot.send_message(callback_query.from_user.id, "Введите ваш ответ. Нажмите 'Завершить ответ' для завершения.", reply_markup=reply_markup)
    await AnswerState.waiting_for_answer.set()

@dp.message_handler(lambda message: message.text == "Завершить ответ", state=AnswerState.waiting_for_answer)
async def finish_answer(message: types.Message, state: FSMContext):
    data = await state.get_data()
    question_id = data['question_id']

    # Удаление вопроса из базы данных
    delete_question(question_id)

    await bot.send_message(message.from_user.id, "Диалог завершен.", reply_markup=admin_menu_keyboard())
    await state.finish()

@dp.message_handler(state=AnswerState.waiting_for_answer)
async def process_answer(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_id = data['current_user_id']
    answer = message.text

    try:
        await bot.send_message(chat_id=user_id, text=f"Администратор ответил на ваш вопрос: {answer}")
        await bot.send_message(chat_id=message.from_user.id, text="Ваш ответ отправлен пользователю.")
    except Exception as e:
        logger.error(f"Ошибка при отправке ответа пользователю {user_id}: {e}")
        await bot.send_message(chat_id=message.from_user.id, text="Произошла ошибка при отправке ответа.")



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
            # Автоматически вызываем команду /start у пользователя
            await bot.send_message(user_id, "Нажми на /start чтобы обновить бота")
        except Exception as e:
            logger.error(f"Error sending message to user {user_id}: {e}")

    elif action == 'reject':
        update_receipt_status(receipt_id, 'rejected')
        await bot.send_message(callback_query.from_user.id, f"Чек {receipt_id} отклонён.")




# Обработчик для кнопок тарифа "Старт"
@dp.message_handler(lambda message: message.text == "🌟 Тариф Старт 🌟")
async def start_tariff_menu(message: types.Message, state: FSMContext):
    keyboard = start_buttons()
    await delete_previous_message(message)
    await bot.send_message(message.from_user.id, "Меню тарифа 'Старт':", reply_markup=keyboard)
    await StartTariffState.in_start_menu.set()



@dp.message_handler(lambda message: message.text == "ChatGPT", state=StartTariffState.in_start_menu)
async def chatgpt(message: types.Message):
    await delete_previous_message(message)
    await bot.send_message(message.from_user.id, "Добро пожаловать в ChatGPT! Задайте ваш вопрос:", reply_markup=back_button())
    await StartTariffState.in_chatgpt.set()

# оброботчик для кнопки назад
@dp.message_handler(lambda message: message.text == "Назад", state=StartTariffState.in_chatgpt)
async def back_to_start_menu_from_chatgpt(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user = check_user_exists(user_id)
    await delete_previous_message(message)
    if user:
        tariff = user[5]
        if tariff == "🌟 Тариф Старт 🌟":
            keyboard = start_buttons()
        elif tariff == "🚀 Тариф Развитие 🚀":
            keyboard = development_buttons()
        elif tariff == "💼 Тариф Профессионал 💼":
            keyboard = professional_buttons()
        await bot.send_message(user_id, "Главный экран:", reply_markup=keyboard)
        await StartTariffState.in_start_menu.set()


@dp.message_handler(state=StartTariffState.in_chatgpt)
async def handle_chatgpt_question(message: types.Message, state: FSMContext):
    user_question = message.text
    await bot.send_message(message.from_user.id, "Ваш вопрос обрабатывается...")

    try:
        answer = generate_response(user_question)
        await bot.send_message(message.from_user.id, answer, reply_markup=back_button())
    except Exception as e:
        await bot.send_message(message.from_user.id, f"Произошла ошибка: {e}", reply_markup=back_button())
        logger.error(f"Error handling ChatGPT question: {e}")


@dp.message_handler(lambda message: message.text == "Связаться с менеджером", state=StartTariffState.in_start_menu)
async def contact_manager(message: types.Message):
    await delete_previous_message(message)
    await bot.send_message(message.from_user.id, "Введите ваш вопрос. В ближайшее время с вами свяжутся.", reply_markup=back_button())
    await PaymentState.waiting_for_question.set()


@dp.message_handler(lambda message: message.text == "Назад", state=StartTariffState.in_profile_menu)
async def back_to_start_menu_from_profile(message: types.Message, state: FSMContext):
    keyboard = start_buttons()
    await delete_previous_message(message)
    await bot.send_message(message.from_user.id, "Главный экран:", reply_markup=keyboard)
    await StartTariffState.in_start_menu.set()

# Обработчик для кнопки "Рассылка"
@dp.message_handler(lambda message: message.text == "📧 Рассылка", state='*')
async def start_broadcast(message: types.Message):
    user_id = message.from_user.id
    if user_id not in ADMINS:
        await bot.send_message(user_id, "У вас нет доступа к этой команде.")
        await delete_previous_message(message)
        return

    await bot.send_message(user_id, "Укажите текст для рассылки:")
    await BroadcastState.waiting_for_text.set()

# Обработчик для ввода текста рассылки
@dp.message_handler(state=BroadcastState.waiting_for_text)
async def process_broadcast_text(message: types.Message, state: FSMContext):
    await state.update_data(text=message.text)
    await delete_previous_message(message)
    await bot.send_message(message.from_user.id, "Укажите медиа рассылки (фото/видео/файл), или отправьте 'Нет', если медиа нет:")
    await BroadcastState.waiting_for_media.set()


# Обработчик для получения медиа или завершения рассылки
@dp.message_handler(content_types=[types.ContentType.PHOTO, types.ContentType.VIDEO, types.ContentType.DOCUMENT, types.ContentType.TEXT], state=BroadcastState.waiting_for_media)
async def process_broadcast_media(message: types.Message, state: FSMContext):
    data = await state.get_data()
    text = data.get('text')

    if message.text and message.text.lower() == 'нет':
        media = None
    elif message.photo:
        media = message.photo[-1].file_id
    elif message.video:
        media = message.video.file_id
    elif message.document:
        media = message.document.file_id
    else:
        media = None

    users = get_all_users()
    for user in users:
        try:
            if media:
                if message.photo:
                    await bot.send_photo(chat_id=user[0], photo=media, caption=text)
                elif message.video:
                    await bot.send_video(chat_id=user[0], video=media, caption=text)
                elif message.document:
                    await bot.send_document(chat_id=user[0], document=media, caption=text)
            else:
                await bot.send_message(chat_id=user[0], text=text)
        except Exception as e:
            logger.error(f"Ошибка при отправке сообщения пользователю {user[0]}: {e}")

    await delete_previous_message(message)
    await bot.send_message(chat_id=message.from_user.id, text="Рассылка успешно отправлена!", reply_markup=admin_menu_keyboard())
    await state.finish()



# Обработчик для кнопки "Назад" в состоянии UpgradeTariffState.in_payment
@dp.message_handler(lambda message: message.text == "Назад", state=UpgradeTariffState.in_payment)
async def back_to_profile_menu_from_upgrade(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user = check_user_exists(user_id)
    if user:
        tariff = user[5]
        if tariff == "🌟 Тариф Старт 🌟":
            await bot.send_message(user_id, "Меню тарифа 'Старт':", reply_markup=start_buttons())
        elif tariff == "🚀 Тариф Развитие 🚀":
            await bot.send_message(user_id, "Меню тарифа 'Развитие':", reply_markup=development_buttons())
        elif tariff == "💼 Тариф Профессионал 💼":
            await bot.send_message(user_id, "Меню тарифа 'Профессионал':", reply_markup=professional_buttons())
    await StartTariffState.in_start_menu.set()


# Обработчик для начала добавления шпаргалки
@dp.message_handler(lambda message: message.text == "➕ Добавить шпаргалку", state='*')
async def add_cheat_sheet(message: types.Message, state: FSMContext):
    if message.from_user.id not in ADMINS:
        await message.reply("У вас нет доступа к этой команде.")
        return

    await CheatSheetState.waiting_for_title.set()
    await message.reply("Введите заголовок шпаргалки:")


# Обработчик для ввода заголовка шпаргалки
@dp.message_handler(state=CheatSheetState.waiting_for_title)
async def process_cheat_sheet_title(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text)
    await CheatSheetState.waiting_for_content.set()
    await message.reply("Введите содержание шпаргалки:")


# Обработчик для ввода содержания шпаргалки
@dp.message_handler(state=CheatSheetState.waiting_for_content)
async def process_cheat_sheet_content(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    title = user_data['title']
    content = message.text

    cheat_sheet_id = save_cheat_sheet(title, content)  # Сохранение шпаргалки в базу данных

    await state.update_data(cheat_sheet_id=cheat_sheet_id)
    await CheatSheetState.waiting_for_files.set()
    await message.reply("Теперь вы можете прикрепить файлы (фото, видео, документы) или напишите 'Нет', если файлы отсутствуют:")


# Обработчик для кнопки "Просмотр шпаргалок"
@dp.message_handler(lambda message: message.text == "🔍 Просмотр шпаргалок", state='*')
async def list_cheat_sheets(message: types.Message):
    if message.from_user.id not in ADMINS:
        await message.reply("У вас нет доступа к этой команде.")
        return

    cheat_sheets = get_cheat_sheets()
    if cheat_sheets:
        for sheet in cheat_sheets:
            response_text = f"ID: {sheet['id']}\nЗаголовок: {sheet['title']}\nСодержание: {sheet['content']}\nФайлы:\n"
            for file in sheet['files']:
                response_text += f" - File ID: {file['file_id']} (Тип: {file['file_type']})\n"
            await message.reply(response_text)

            media = []
            documents = []
            for file in sheet['files']:
                if file['file_type'] == 'photo':
                    media.append(types.InputMediaPhoto(media=file['file_id']))
                elif file['file_type'] == 'video':
                    media.append(types.InputMediaVideo(media=file['file_id']))
                elif file['file_type'] == 'document':
                    documents.append(file['file_id'])

            if media:
                await bot.send_media_group(message.chat.id, media=media)

            for doc in documents:
                await bot.send_document(message.chat.id, document=doc)
    else:
        await message.reply("Нет добавленных шпаргалок.")

@dp.message_handler(content_types=[types.ContentType.PHOTO, types.ContentType.VIDEO, types.ContentType.DOCUMENT, types.ContentType.TEXT], state=CheatSheetState.waiting_for_files)
async def process_cheat_sheet_files(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    cheat_sheet_id = user_data['cheat_sheet_id']

    if message.text and message.text.lower() == 'нет':
        await state.finish()
        await message.reply("Шпаргалка успешно добавлена.", reply_markup=admin_menu_keyboard())
        return

    if message.photo:
        file_id = message.photo[-1].file_id
        file_type = 'photo'
    elif message.video:
        file_id = message.video.file_id
        file_type = 'video'
    elif message.document:
        file_id = message.document.file_id
        file_type = 'document'
    else:
        return

    save_cheat_sheet_file(cheat_sheet_id, file_id, file_type)  # Сохранение файла в базу данных

    await message.reply("Файл добавлен. Вы можете добавить еще файлы или напишите 'Нет', если файлов больше нет.")


@dp.message_handler(lambda message: message.text == "Полезные материалы", state=StartTariffState.in_start_menu)
async def useful_materials(message: types.Message):
    cheat_sheets = get_cheat_sheets()
    if cheat_sheets:
        for sheet in cheat_sheets:
            response_text = f"Заголовок: {sheet['title']}\nСодержание: {sheet['content']}"
            await message.reply(response_text)

            media = []
            documents = []
            for file in sheet['files']:
                if file['file_type'] == 'photo':
                    media.append(types.InputMediaPhoto(media=file['file_id']))
                elif file['file_type'] == 'video':
                    media.append(types.InputMediaVideo(media=file['file_id']))
                elif file['file_type'] == 'document':
                    documents.append(file['file_id'])

            if media:
                await bot.send_media_group(message.chat.id, media=media)

            for doc in documents:
                await bot.send_document(message.chat.id, document=doc)
    else:
        await message.reply("Нет доступных шпаргалок.")


# Обработчик для начала редактирования шпаргалки
@dp.message_handler(lambda message: message.text == "✏️ Редактировать шпаргалку", state='*')
async def choose_cheat_sheet_to_edit(message: types.Message, state: FSMContext):
    if message.from_user.id not in ADMINS:
        await message.reply("У вас нет доступа к этой команде.")
        return

    cheat_sheets = get_cheat_sheets()
    if cheat_sheets:
        buttons = [InlineKeyboardButton(sheet['title'], callback_data=f"edit_{sheet['id']}") for sheet in cheat_sheets]
        keyboard = InlineKeyboardMarkup(row_width=1)
        keyboard.add(*buttons)
        await message.reply("Выберите шпаргалку для редактирования:", reply_markup=keyboard)
    else:
        await message.reply("Нет добавленных шпаргалок.")


# Обработчик для выбора шпаргалки для редактирования
@dp.callback_query_handler(lambda c: c.data.startswith('edit_'), state='*')
async def edit_cheat_sheet(callback_query: types.CallbackQuery, state: FSMContext):
    cheat_sheet_id = int(callback_query.data.split('_')[1])
    await state.update_data(cheat_sheet_id=cheat_sheet_id)

    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(InlineKeyboardButton('Изменить заголовок', callback_data='edit_title'))
    keyboard.add(InlineKeyboardButton('Изменить содержание', callback_data='edit_content'))
    keyboard.add(InlineKeyboardButton('Удалить файлы', callback_data='remove_files'))
    keyboard.add(InlineKeyboardButton('Удалить шпаргалку', callback_data='delete_cheat_sheet'))

    await bot.send_message(callback_query.from_user.id, "Что вы хотите изменить?", reply_markup=keyboard)
    await CheatSheetState.waiting_for_edit_choice.set()


# Обработчик для изменения заголовка шпаргалки
@dp.callback_query_handler(lambda c: c.data == 'edit_title', state=CheatSheetState.waiting_for_edit_choice)
async def edit_cheat_sheet_title(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.send_message(callback_query.from_user.id, "Введите новый заголовок шпаргалки:")
    await CheatSheetState.waiting_for_new_title.set()


@dp.message_handler(state=CheatSheetState.waiting_for_new_title)
async def process_new_cheat_sheet_title(message: types.Message, state: FSMContext):
    new_title = message.text
    user_data = await state.get_data()
    cheat_sheet_id = user_data['cheat_sheet_id']
    cheat_sheet = get_cheat_sheet_by_id(cheat_sheet_id)
    update_cheat_sheet(cheat_sheet_id, new_title, cheat_sheet['content'])
    await state.finish()
    await message.reply("Заголовок шпаргалки обновлен.", reply_markup=admin_menu_keyboard())


# Обработчик для изменения содержания шпаргалки
@dp.callback_query_handler(lambda c: c.data == 'edit_content', state=CheatSheetState.waiting_for_edit_choice)
async def edit_cheat_sheet_content(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.send_message(callback_query.from_user.id, "Введите новое содержание шпаргалки:")
    await CheatSheetState.waiting_for_new_content.set()


@dp.message_handler(state=CheatSheetState.waiting_for_new_content)
async def process_new_cheat_sheet_content(message: types.Message, state: FSMContext):
    new_content = message.text
    user_data = await state.get_data()
    cheat_sheet_id = user_data['cheat_sheet_id']
    cheat_sheet = get_cheat_sheet_by_id(cheat_sheet_id)
    update_cheat_sheet(cheat_sheet_id, cheat_sheet['title'], new_content)
    await state.finish()
    await message.reply("Содержание шпаргалки обновлено.", reply_markup=admin_menu_keyboard())


# Обработчик для удаления файлов из шпаргалки
@dp.callback_query_handler(lambda c: c.data == 'remove_files', state=CheatSheetState.waiting_for_edit_choice)
async def choose_file_to_remove(callback_query: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    cheat_sheet_id = user_data['cheat_sheet_id']
    cheat_sheet = get_cheat_sheet_by_id(cheat_sheet_id)

    buttons = [InlineKeyboardButton(f"{file['file_type']}", callback_data=f"remove_file_{file['id']}") for file in
               cheat_sheet['files']]
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(*buttons)
    await bot.send_message(callback_query.from_user.id, "Выберите файл для удаления:", reply_markup=keyboard)
    await CheatSheetState.waiting_for_file_removal.set()


@dp.callback_query_handler(lambda c: c.data.startswith('remove_file_'), state=CheatSheetState.waiting_for_file_removal)
async def remove_file_from_cheat_sheet(callback_query: types.CallbackQuery, state: FSMContext):
    file_id = int(callback_query.data.split('_')[2])
    delete_cheat_sheet_file(file_id)
    await state.finish()
    await bot.send_message(callback_query.from_user.id, "Файл удален.", reply_markup=admin_menu_keyboard())


# Обработчик для удаления шпаргалки
@dp.callback_query_handler(lambda c: c.data == 'delete_cheat_sheet', state=CheatSheetState.waiting_for_edit_choice)
async def delete_cheat_sheet_handler(callback_query: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    cheat_sheet_id = user_data['cheat_sheet_id']
    delete_cheat_sheet(cheat_sheet_id)
    await state.finish()
    await bot.send_message(callback_query.from_user.id, "Шпаргалка удалена.", reply_markup=admin_menu_keyboard())

@dp.message_handler(lambda message: message.text == "➕ Добавить администратора", state='*')
async def add_admin_start(message: types.Message):
    if message.from_user.id not in ADMINS:
        await message.reply("У вас нет доступа к этой команде.")
        return

    await AddAdminState.waiting_for_admin_id.set()
    await message.reply("Пожалуйста, введите ID нового администратора:")


@dp.message_handler(state=AddAdminState.waiting_for_admin_id)
async def process_new_admin_id(message: types.Message, state: FSMContext):
    try:
        new_admin_id = int(message.text)
        ADMINS.append(new_admin_id)  # Добавление нового администратора в список
        await state.finish()
        await message.reply(f"ID {new_admin_id} успешно добавлен в список администраторов.", reply_markup=admin_menu_keyboard())
    except ValueError:
        await message.reply("Пожалуйста, введите корректный числовой ID.")
