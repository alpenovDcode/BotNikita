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

class BusinessQuestionsState(StatesGroup):
    Q1 = State()
    Q2 = State()
    Q3 = State()
    Q4 = State()
    Q5 = State()
    Q6 = State()
    Q7 = State()
    Q8 = State()
    Q9 = State()

class CheatSheetState(StatesGroup):
    waiting_for_title = State()
    waiting_for_content = State()
    waiting_for_files = State()
    waiting_for_edit_choice = State()
    waiting_for_new_title = State()
    waiting_for_new_content = State()
    waiting_for_file_removal = State()

class AddAdminState(StatesGroup):
    waiting_for_admin_id = State()

