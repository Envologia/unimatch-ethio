from aiogram import types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from database.database import get_session
from database.models import User
from config import MIN_AGE, MAX_AGE
from .keyboards import get_profile_edit_keyboard, get_university_keyboard
from .states import ProfileStates, EditProfileStates

async def view_profile(message: types.Message):
    """View user's profile."""
    session = get_session()
    user = session.query(User).filter_by(telegram_id=message.from_user.id).first()
    
    if not user:
        await message.answer(
            "You haven't created a profile yet! Use /create_profile to get started."
        )
        return
    
    profile_text = (
        f"👤 Your Profile:\n\n"
        f"Age: {user.age}\n"
        f"Gender: {user.gender}\n"
        f"University: {user.university}\n"
        f"Bio: {user.bio}\n"
        f"Hobbies: {user.hobbies}\n\n"
        f"Last updated: {user.last_updated.strftime('%Y-%m-%d %H:%M')}"
    )
    
    keyboard = get_profile_edit_keyboard()
    await message.answer(profile_text, reply_markup=keyboard)
    session.close()

async def start_profile_edit(callback: types.CallbackQuery, state: FSMContext):
    """Start the profile editing process."""
    await callback.message.answer(
        "What would you like to edit?",
        reply_markup=get_profile_edit_keyboard()
    )
    await state.set_state(EditProfileStates.waiting_for_field)
    await callback.answer()

async def process_edit_field(callback: types.CallbackQuery, state: FSMContext):
    """Process the field selection for editing."""
    field = callback.data.split("_")[1]
    await state.update_data(edit_field=field)
    
    if field == "age":
        await callback.message.answer(f"Please enter your new age ({MIN_AGE}-{MAX_AGE}):")
        await state.set_state(EditProfileStates.waiting_for_age)
    elif field == "gender":
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Male", callback_data="gender_male")],
            [InlineKeyboardButton(text="Female", callback_data="gender_female")],
        ])
        await callback.message.answer("Please select your gender:", reply_markup=keyboard)
        await state.set_state(EditProfileStates.waiting_for_gender)
    elif field == "university":
        await callback.message.answer(
            "Please select your university:",
            reply_markup=get_university_keyboard()
        )
        await state.set_state(EditProfileStates.waiting_for_university)
    elif field == "bio":
        await callback.message.answer("Please write your new bio:")
        await state.set_state(EditProfileStates.waiting_for_bio)
    elif field == "hobbies":
        await callback.message.answer("Please list your new hobbies (comma-separated):")
        await state.set_state(EditProfileStates.waiting_for_hobbies)
    elif field == "photo":
        await callback.message.answer("Please send your new profile picture:")
        await state.set_state(EditProfileStates.waiting_for_photo)
    
    await callback.answer()

async def save_gender(callback: types.CallbackQuery, state: FSMContext):
    """Save the selected gender."""
    gender = callback.data.split("_")[1]
    session = get_session()
    user = session.query(User).filter_by(telegram_id=callback.from_user.id).first()
    
    if user:
        user.gender = gender
        session.commit()
        await callback.message.answer("✅ Gender updated successfully!")
    else:
        await callback.message.answer("Error: Profile not found!")
    
    session.close()
    await state.clear()
    await view_profile(callback.message)

async def save_university(callback: types.CallbackQuery, state: FSMContext):
    """Save the selected university."""
    university = callback.data.split("_")[1]
    session = get_session()
    user = session.query(User).filter_by(telegram_id=callback.from_user.id).first()
    
    if user:
        user.university = university
        session.commit()
        await callback.message.answer("✅ University updated successfully!")
    else:
        await callback.message.answer("Error: Profile not found!")
    
    session.close()
    await state.clear()
    await view_profile(callback.message)

async def save_edit(message: types.Message, state: FSMContext):
    """Save the edited profile field."""
    data = await state.get_data()
    field = data.get('edit_field')
    
    session = get_session()
    user = session.query(User).filter_by(telegram_id=message.from_user.id).first()
    
    if not user:
        await message.answer("Error: Profile not found!")
        await state.clear()
        return
    
    if field == "age":
        try:
            age = int(message.text)
            if MIN_AGE <= age <= MAX_AGE:
                user.age = age
            else:
                await message.answer(f"Please enter an age between {MIN_AGE} and {MAX_AGE}.")
                return
        except ValueError:
            await message.answer("Please enter a valid number for your age.")
            return
    elif field == "bio":
        user.bio = message.text
    elif field == "hobbies":
        user.hobbies = message.text
    
    session.commit()
    session.close()
    
    await message.answer("✅ Profile updated successfully!")
    await state.clear()
    await view_profile(message)

async def save_photo_edit(message: types.Message, state: FSMContext):
    """Save the edited profile photo."""
    photo = message.photo[-1]
    file_id = photo.file_id
    
    session = get_session()
    user = session.query(User).filter_by(telegram_id=message.from_user.id).first()
    
    if user:
        user.profile_picture = file_id
        session.commit()
        await message.answer("✅ Profile picture updated successfully!")
    else:
        await message.answer("Error: Profile not found!")
    
    session.close()
    await state.clear()
    await view_profile(message)

def register_profile_handlers(dp):
    """Register all profile-related handlers."""
    dp.message.register(view_profile, Command("profile"))
    dp.callback_query.register(start_profile_edit, F.data == "edit_profile")
    dp.callback_query.register(process_edit_field, EditProfileStates.waiting_for_field)
    dp.callback_query.register(save_gender, EditProfileStates.waiting_for_gender)
    dp.callback_query.register(save_university, EditProfileStates.waiting_for_university)
    dp.message.register(save_edit, EditProfileStates.waiting_for_age)
    dp.message.register(save_edit, EditProfileStates.waiting_for_bio)
    dp.message.register(save_edit, EditProfileStates.waiting_for_hobbies)
    dp.message.register(save_photo_edit, EditProfileStates.waiting_for_photo, F.photo) 