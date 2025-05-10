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

class MatchStates(StatesGroup):
    """States for matching process."""
    viewing_matches = State()
    waiting_for_match_choice = State()

class ConfessionStates(StatesGroup):
    """States for confession process."""
    waiting_for_confession = State()
    waiting_for_moderation = State()

class ChannelStates(StatesGroup):
    """States for channel operations."""
    waiting_for_post = State()
    waiting_for_verification = State()

class ReportStates(StatesGroup):
    """States for reporting process."""
    waiting_for_reason = State()
    waiting_for_confirmation = State() 