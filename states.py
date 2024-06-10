from aiogram.dispatcher.filters.state import State, StatesGroup

class RegisterState(StatesGroup):
    waiting_for_name = State()
    waiting_for_password = State()

class PaymentState(StatesGroup):
    waiting_for_receipt = State()
    waiting_for_question = State()

class StartTariffState(StatesGroup):
    in_start_menu = State()
    in_profile_menu = State()
    in_chatgpt = State()

class UpgradeTariffState(StatesGroup):
    waiting_for_new_tariff = State()
    in_payment = State()

class BroadcastState(StatesGroup):
    waiting_for_text = State()
    waiting_for_media = State()

class AnswerState(StatesGroup):
    waiting_for_answer = State()
    current_user_id = State()

class EditProfileState(StatesGroup):
    waiting_for_new_name = State()
    waiting_for_new_contact = State()