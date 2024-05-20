from aiogram.dispatcher.filters.state import State, StatesGroup

class AuthState(StatesGroup):
    waiting_for_username = State()
    waiting_for_password = State()

class RegisterState(StatesGroup):
    waiting_for_name = State()
    waiting_for_password = State()