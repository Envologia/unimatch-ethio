from aiogram import types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from datetime import datetime
import logging

from database.database import get_session
from database.models import User, Gender
from config import (
    MIN_AGE, MAX_AGE, MAX_BIO_LENGTH, MAX_HOBBIES_LENGTH,
    ERROR_MESSAGES
)
from .keyboards import (
    get_profile_edit_keyboard, get_university_keyboard,
    get_gender_keyboard, get_main_menu_keyboard
)
from .states import ProfileStates, EditProfileStates

logger = logging.getLogger(__name__)

async def start_profile(message: types.Message, state: FSMContext):
    """Start the profile creation process."""
    try:
        with get_session() as session:
            # Check if profile already exists
            existing_user = session.query(User).filter_by(telegram_id=message.from_user.id).first()
            if existing_user:
                await message.answer(
                    "You already have a profile. Use /edit to modify it.",
                    reply_markup=get_profile_edit_keyboard()
                )
                return

            # Start profile creation
            await message.answer(
                f"Let's create your profile! First, how old are you? (Between {MIN_AGE} and {MAX_AGE})"
            )
            await state.set_state(ProfileStates.waiting_for_age)
    except Exception as e:
        logger.error(f"Error in start_profile: {e}")
        await message.answer(ERROR_MESSAGES['database_error'])
        await state.clear()

async def process_age(message: types.Message, state: FSMContext):
    """Process user's age input."""
    try:
        age = int(message.text)
        if not MIN_AGE <= age <= MAX_AGE:
            await message.answer(ERROR_MESSAGES['invalid_age'])
            return

        await state.update_data(age=age)
        await message.answer(
            "Great! Now, what's your gender?",
            reply_markup=get_gender_keyboard()
        )
        await state.set_state(ProfileStates.waiting_for_gender)
    except ValueError:
        await message.answer("Please enter a valid number.")
    except Exception as e:
        logger.error(f"Error in process_age: {e}")
        await message.answer(ERROR_MESSAGES['invalid_input'])
        await state.clear()

async def process_gender(callback: types.CallbackQuery, state: FSMContext):
    """Process user's gender selection."""
    try:
        gender = callback.data.split(':')[1]
        if gender not in [g.value for g in Gender]:
            await callback.answer(ERROR_MESSAGES['invalid_gender'])
            return

        await state.update_data(gender=gender)
        await callback.message.answer(
            "Which university do you attend?",
            reply_markup=get_university_keyboard()
        )
        await state.set_state(ProfileStates.waiting_for_university)
        await callback.answer()
    except Exception as e:
        logger.error(f"Error in process_gender: {e}")
        await callback.message.answer(ERROR_MESSAGES['invalid_input'])
        await state.clear()

async def process_university(callback: types.CallbackQuery, state: FSMContext):
    """Process user's university selection."""
    try:
        university = callback.data.split(':')[1]
        await state.update_data(university=university)
        await callback.message.answer(
            f"Tell us about yourself (max {MAX_BIO_LENGTH} characters):"
        )
        await state.set_state(ProfileStates.waiting_for_bio)
        await callback.answer()
    except Exception as e:
        logger.error(f"Error in process_university: {e}")
        await callback.message.answer(ERROR_MESSAGES['invalid_input'])
        await state.clear()

async def process_bio(message: types.Message, state: FSMContext):
    """Process user's bio input."""
    try:
        if len(message.text) > MAX_BIO_LENGTH:
            await message.answer(ERROR_MESSAGES['bio_too_long'])
            return

        await state.update_data(bio=message.text)
        await message.answer(
            f"What are your hobbies? (max {MAX_HOBBIES_LENGTH} characters):"
        )
        await state.set_state(ProfileStates.waiting_for_hobbies)
    except Exception as e:
        logger.error(f"Error in process_bio: {e}")
        await message.answer(ERROR_MESSAGES['invalid_input'])
        await state.clear()

async def process_hobbies(message: types.Message, state: FSMContext):
    """Process user's hobbies input."""
    try:
        if len(message.text) > MAX_HOBBIES_LENGTH:
            await message.answer(ERROR_MESSAGES['hobbies_too_long'])
            return

        await state.update_data(hobbies=message.text)
        await message.answer(
            "Finally, send us a photo of yourself:"
        )
        await state.set_state(ProfileStates.waiting_for_photo)
    except Exception as e:
        logger.error(f"Error in process_hobbies: {e}")
        await message.answer(ERROR_MESSAGES['invalid_input'])
        await state.clear()

async def process_photo(message: types.Message, state: FSMContext):
    """Process user's photo input."""
    try:
        if not message.photo:
            await message.answer("Please send a photo.")
            return

        photo_id = message.photo[-1].file_id
        data = await state.get_data()
        
        with get_session() as session:
            user = User(
                telegram_id=message.from_user.id,
                username=message.from_user.username,
                first_name=message.from_user.first_name,
                last_name=message.from_user.last_name,
                age=data['age'],
                gender=data['gender'],
                university=data['university'],
                bio=data['bio'],
                hobbies=data['hobbies'],
                photo_id=photo_id
            )
            session.add(user)

        await message.answer(
            "✅ Your profile has been created!",
            reply_markup=get_main_menu_keyboard()
        )
        await state.clear()
    except Exception as e:
        logger.error(f"Error in process_photo: {e}")
        await message.answer(ERROR_MESSAGES['database_error'])
        await state.clear()

async def view_profile(message: types.Message):
    """View user's profile."""
    try:
        with get_session() as session:
            user = session.query(User).filter_by(telegram_id=message.from_user.id).first()
            if not user:
                await message.answer(ERROR_MESSAGES['profile_required'])
                return

            profile_text = format_profile(user)
            if user.photo_id:
                await message.answer_photo(
                    photo=user.photo_id,
                    caption=profile_text,
                    reply_markup=get_profile_edit_keyboard()
                )
            else:
                await message.answer(
                    text=profile_text,
                    reply_markup=get_profile_edit_keyboard()
                )
    except Exception as e:
        logger.error(f"Error in view_profile: {e}")
        await message.answer(ERROR_MESSAGES['database_error'])

async def start_profile_edit(message: types.Message, state: FSMContext):
    """Start the profile editing process."""
    try:
        with get_session() as session:
            user = session.query(User).filter_by(telegram_id=message.from_user.id).first()
            if not user:
                await message.answer(ERROR_MESSAGES['profile_required'])
                return

            await message.answer(
                "What would you like to edit?",
                reply_markup=get_profile_edit_keyboard()
            )
            await state.set_state(EditProfileStates.waiting_for_field)
    except Exception as e:
        logger.error(f"Error in start_profile_edit: {e}")
        await message.answer(ERROR_MESSAGES['database_error'])
        await state.clear()

async def process_edit_field(callback: types.CallbackQuery, state: FSMContext):
    """Process which field to edit."""
    try:
        field = callback.data.split('_')[1]
        await state.update_data(edit_field=field)

        if field == 'age':
            await callback.message.answer(
                f"Enter your new age (between {MIN_AGE} and {MAX_AGE}):"
            )
            await state.set_state(EditProfileStates.waiting_for_age)
        elif field == 'gender':
            await callback.message.answer(
                "Select your gender:",
                reply_markup=get_gender_keyboard()
            )
            await state.set_state(EditProfileStates.waiting_for_gender)
        elif field == 'university':
            await callback.message.answer(
                "Select your university:",
                reply_markup=get_university_keyboard()
            )
            await state.set_state(EditProfileStates.waiting_for_university)
        elif field == 'bio':
            await callback.message.answer(
                f"Enter your new bio (max {MAX_BIO_LENGTH} characters):"
            )
            await state.set_state(EditProfileStates.waiting_for_bio)
        elif field == 'hobbies':
            await callback.message.answer(
                f"Enter your new hobbies (max {MAX_HOBBIES_LENGTH} characters):"
            )
            await state.set_state(EditProfileStates.waiting_for_hobbies)
        elif field == 'photo':
            await callback.message.answer("Send your new photo:")
            await state.set_state(EditProfileStates.waiting_for_photo)
        elif field == 'delete':
            await callback.message.answer(
                "Are you sure you want to delete your profile? This cannot be undone!",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [
                        InlineKeyboardButton(text="✅ Yes", callback_data="confirm_delete"),
                        InlineKeyboardButton(text="❌ No", callback_data="cancel_delete")
                    ]
                ])
            )
            await state.set_state(EditProfileStates.waiting_for_confirmation)

        await callback.answer()
    except Exception as e:
        logger.error(f"Error in process_edit_field: {e}")
        await callback.message.answer(ERROR_MESSAGES['invalid_input'])
        await state.clear()

async def save_edit(message: types.Message, state: FSMContext):
    """Save edited profile field."""
    try:
        data = await state.get_data()
        field = data['edit_field']
        value = message.text

        with get_session() as session:
            user = session.query(User).filter_by(telegram_id=message.from_user.id).first()
            if not user:
                await message.answer(ERROR_MESSAGES['profile_required'])
                return

            if field == 'age':
                age = int(value)
                if not MIN_AGE <= age <= MAX_AGE:
                    await message.answer(ERROR_MESSAGES['invalid_age'])
                    return
                user.age = age
            elif field == 'bio':
                if len(value) > MAX_BIO_LENGTH:
                    await message.answer(ERROR_MESSAGES['bio_too_long'])
                    return
                user.bio = value
            elif field == 'hobbies':
                if len(value) > MAX_HOBBIES_LENGTH:
                    await message.answer(ERROR_MESSAGES['hobbies_too_long'])
                    return
                user.hobbies = value

            user.updated_at = datetime.utcnow()

        await message.answer(
            "✅ Profile updated successfully!",
            reply_markup=get_main_menu_keyboard()
        )
        await state.clear()
    except ValueError:
        await message.answer("Please enter a valid number.")
    except Exception as e:
        logger.error(f"Error in save_edit: {e}")
        await message.answer(ERROR_MESSAGES['database_error'])
        await state.clear()

async def save_photo_edit(message: types.Message, state: FSMContext):
    """Save edited profile photo."""
    try:
        if not message.photo:
            await message.answer("Please send a photo.")
            return

        photo_id = message.photo[-1].file_id
        
        with get_session() as session:
            user = session.query(User).filter_by(telegram_id=message.from_user.id).first()
            if not user:
                await message.answer(ERROR_MESSAGES['profile_required'])
                return

            user.photo_id = photo_id
            user.updated_at = datetime.utcnow()

        await message.answer(
            "✅ Profile photo updated successfully!",
            reply_markup=get_main_menu_keyboard()
        )
        await state.clear()
    except Exception as e:
        logger.error(f"Error in save_photo_edit: {e}")
        await message.answer(ERROR_MESSAGES['database_error'])
        await state.clear()

async def save_gender_edit(callback: types.CallbackQuery, state: FSMContext):
    """Save edited gender."""
    try:
        gender = callback.data.split(':')[1]
        if gender not in [g.value for g in Gender]:
            await callback.answer(ERROR_MESSAGES['invalid_gender'])
            return

        with get_session() as session:
            user = session.query(User).filter_by(telegram_id=callback.from_user.id).first()
            if not user:
                await callback.message.answer(ERROR_MESSAGES['profile_required'])
                return

            user.gender = gender
            user.updated_at = datetime.utcnow()

        await callback.message.answer(
            "✅ Gender updated successfully!",
            reply_markup=get_main_menu_keyboard()
        )
        await state.clear()
        await callback.answer()
    except Exception as e:
        logger.error(f"Error in save_gender_edit: {e}")
        await callback.message.answer(ERROR_MESSAGES['database_error'])
        await state.clear()

async def save_university_edit(callback: types.CallbackQuery, state: FSMContext):
    """Save edited university."""
    try:
        university = callback.data.split(':')[1]
        
        with get_session() as session:
            user = session.query(User).filter_by(telegram_id=callback.from_user.id).first()
            if not user:
                await callback.message.answer(ERROR_MESSAGES['profile_required'])
                return

            user.university = university
            user.updated_at = datetime.utcnow()

        await callback.message.answer(
            "✅ University updated successfully!",
            reply_markup=get_main_menu_keyboard()
        )
        await state.clear()
        await callback.answer()
    except Exception as e:
        logger.error(f"Error in save_university_edit: {e}")
        await callback.message.answer(ERROR_MESSAGES['database_error'])
        await state.clear()

async def delete_profile(callback: types.CallbackQuery, state: FSMContext):
    """Delete user's profile."""
    try:
        if callback.data != "confirm_delete":
            await callback.message.answer(
                "Profile deletion cancelled.",
                reply_markup=get_main_menu_keyboard()
            )
            await state.clear()
            return

        with get_session() as session:
            user = session.query(User).filter_by(telegram_id=callback.from_user.id).first()
            if user:
                session.delete(user)

        await callback.message.answer(
            "Your profile has been deleted.",
            reply_markup=get_main_menu_keyboard()
        )
        await state.clear()
        await callback.answer()
    except Exception as e:
        logger.error(f"Error in delete_profile: {e}")
        await callback.message.answer(ERROR_MESSAGES['database_error'])
        await state.clear()

def format_profile(user: User) -> str:
    """Format user profile for display."""
    return (
        f"👤 Profile\n\n"
        f"Name: {user.first_name} {user.last_name or ''}\n"
        f"Age: {user.age}\n"
        f"Gender: {user.gender.value}\n"
        f"University: {user.university}\n"
        f"Bio: {user.bio}\n"
        f"Hobbies: {user.hobbies}\n\n"
        f"Last updated: {user.updated_at.strftime('%Y-%m-%d %H:%M')}"
    )

def register_profile_handlers(dp):
    """Register all profile-related handlers."""
    dp.message.register(start_profile, Command("profile"))
    dp.message.register(process_age, ProfileStates.waiting_for_age)
    dp.callback_query.register(process_gender, F.data.startswith("gender:"), ProfileStates.waiting_for_gender)
    dp.callback_query.register(process_university, F.data.startswith("university:"), ProfileStates.waiting_for_university)
    dp.message.register(process_bio, ProfileStates.waiting_for_bio)
    dp.message.register(process_hobbies, ProfileStates.waiting_for_hobbies)
    dp.message.register(process_photo, ProfileStates.waiting_for_photo)
    
    dp.message.register(view_profile, Command("view"))
    dp.message.register(start_profile_edit, Command("edit"))
    dp.callback_query.register(process_edit_field, F.data.startswith("edit_"), EditProfileStates.waiting_for_field)
    dp.message.register(save_edit, EditProfileStates.waiting_for_age)
    dp.message.register(save_edit, EditProfileStates.waiting_for_bio)
    dp.message.register(save_edit, EditProfileStates.waiting_for_hobbies)
    dp.message.register(save_photo_edit, EditProfileStates.waiting_for_photo)
    dp.callback_query.register(save_gender_edit, F.data.startswith("gender:"), EditProfileStates.waiting_for_gender)
    dp.callback_query.register(save_university_edit, F.data.startswith("university:"), EditProfileStates.waiting_for_university)
    dp.callback_query.register(delete_profile, F.data.in_(["confirm_delete", "cancel_delete"]), EditProfileStates.waiting_for_confirmation) 