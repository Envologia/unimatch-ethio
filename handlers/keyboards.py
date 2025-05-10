from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from universities import ETHIOPIAN_UNIVERSITIES

def get_profile_edit_keyboard() -> InlineKeyboardMarkup:
    """Create keyboard for profile editing options."""
    keyboard = [
        [InlineKeyboardButton(text="Edit Age", callback_data="edit_age")],
        [InlineKeyboardButton(text="Edit Gender", callback_data="edit_gender")],
        [InlineKeyboardButton(text="Edit University", callback_data="edit_university")],
        [InlineKeyboardButton(text="Edit Department", callback_data="edit_department")],
        [InlineKeyboardButton(text="Edit Bio", callback_data="edit_bio")],
        [InlineKeyboardButton(text="Edit Hobbies", callback_data="edit_hobbies")],
        [InlineKeyboardButton(text="Edit Photo", callback_data="edit_photo")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_university_keyboard() -> InlineKeyboardMarkup:
    """Create keyboard with university options."""
    keyboard = []
    for university in ETHIOPIAN_UNIVERSITIES.keys():
        keyboard.append([InlineKeyboardButton(text=university, callback_data=f"university_{university}")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_department_keyboard(university: str) -> InlineKeyboardMarkup:
    """Create keyboard with department options for a university."""
    keyboard = []
    for department in ETHIOPIAN_UNIVERSITIES[university]:
        keyboard.append([InlineKeyboardButton(text=department, callback_data=f"department_{department}")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    """Create main menu keyboard."""
    keyboard = [
        [InlineKeyboardButton(text="Create Profile", callback_data="create_profile")],
        [InlineKeyboardButton(text="View Profile", callback_data="view_profile")],
        [InlineKeyboardButton(text="Find Matches", callback_data="find_matches")],
        [InlineKeyboardButton(text="Confessions", callback_data="confessions")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard) 