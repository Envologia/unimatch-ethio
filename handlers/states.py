from aiogram.fsm.state import State, StatesGroup

class ProfileStates(StatesGroup):
    """States for profile creation."""
    waiting_for_age = State()
    waiting_for_gender = State()
    waiting_for_university = State()
    waiting_for_bio = State()
    waiting_for_hobbies = State()
    waiting_for_photo = State()

class EditProfileStates(StatesGroup):
    """States for profile editing."""
    waiting_for_field = State()
    waiting_for_age = State()
    waiting_for_gender = State()
    waiting_for_university = State()
    waiting_for_bio = State()
    waiting_for_hobbies = State()
    waiting_for_photo = State() 