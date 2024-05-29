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

class UpgradeTariffState(StatesGroup):
    waiting_for_new_tariff = State()
