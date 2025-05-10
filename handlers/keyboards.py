from aiogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton
)
from config import ETHIOPIAN_UNIVERSITIES

def get_profile_edit_keyboard() -> InlineKeyboardMarkup:
    """Create keyboard for profile editing options."""
    keyboard = [
        [
            InlineKeyboardButton(text="👤 Age", callback_data="edit_age"),
            InlineKeyboardButton(text="⚧ Gender", callback_data="edit_gender")
        ],
        [
            InlineKeyboardButton(text="🎓 University", callback_data="edit_university"),
            InlineKeyboardButton(text="📝 Bio", callback_data="edit_bio")
        ],
        [
            InlineKeyboardButton(text="🎯 Hobbies", callback_data="edit_hobbies"),
            InlineKeyboardButton(text="📸 Photo", callback_data="edit_photo")
        ],
        [
            InlineKeyboardButton(text="❌ Delete Profile", callback_data="delete_profile")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_university_keyboard() -> InlineKeyboardMarkup:
    """Create keyboard with university options."""
    keyboard = [
        [InlineKeyboardButton(text=university, callback_data=f"university:{university}")]
        for university in ETHIOPIAN_UNIVERSITIES
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_department_keyboard(university: str) -> InlineKeyboardMarkup:
    """Create keyboard with department options for a university."""
    keyboard = []
    for department in ETHIOPIAN_UNIVERSITIES[university]:
        keyboard.append([InlineKeyboardButton(text=department, callback_data=f"department_{department}")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_gender_keyboard() -> InlineKeyboardMarkup:
    """Create keyboard for gender selection."""
    keyboard = [
        [
            InlineKeyboardButton(text="👨 Male", callback_data="gender:male"),
            InlineKeyboardButton(text="👩 Female", callback_data="gender:female")
        ],
        [
            InlineKeyboardButton(text="⚧ Other", callback_data="gender:other")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_main_menu_keyboard() -> ReplyKeyboardMarkup:
    """Create main menu keyboard."""
    keyboard = [
        [
            KeyboardButton(text="👤 Profile"),
            KeyboardButton(text="💝 Find Matches")
        ],
        [
            KeyboardButton(text="💭 Confessions"),
            KeyboardButton(text="❓ Help")
        ]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

def get_match_keyboard(user_id: int) -> InlineKeyboardMarkup:
    """Create keyboard for match actions."""
    keyboard = [
        [
            InlineKeyboardButton(text="❤️ Like", callback_data=f"like:{user_id}"),
            InlineKeyboardButton(text="⏭️ Skip", callback_data=f"skip:{user_id}")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_unmatch_keyboard(user_id: int) -> InlineKeyboardMarkup:
    """Create keyboard for unmatch actions."""
    keyboard = [
        [
            InlineKeyboardButton(text="❌ Unmatch", callback_data=f"unmatch:{user_id}")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_confession_keyboard() -> InlineKeyboardMarkup:
    """Create keyboard for confession actions."""
    keyboard = [
        [
            InlineKeyboardButton(text="💭 New Confession", callback_data="new_confession"),
            InlineKeyboardButton(text="📋 My Confessions", callback_data="my_confessions")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_report_keyboard(user_id: int) -> InlineKeyboardMarkup:
    """Create keyboard for reporting users."""
    keyboard = [
        [
            InlineKeyboardButton(text="🚫 Report User", callback_data=f"report:{user_id}")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_verification_keyboard() -> InlineKeyboardMarkup:
    """Create keyboard for channel verification."""
    keyboard = [
        [
            InlineKeyboardButton(text="✅ Verify Membership", callback_data="verify_membership")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_admin_keyboard() -> InlineKeyboardMarkup:
    """Create keyboard for admin actions."""
    keyboard = [
        [
            InlineKeyboardButton(text="📢 Post to Channel", callback_data="post_to_channel"),
            InlineKeyboardButton(text="👥 View Users", callback_data="view_users")
        ],
        [
            InlineKeyboardButton(text="📋 View Reports", callback_data="view_reports"),
            InlineKeyboardButton(text="⚙️ Settings", callback_data="admin_settings")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard) 