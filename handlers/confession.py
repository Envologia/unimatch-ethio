from aiogram import types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from datetime import datetime
import logging
from typing import Optional

from database.database import get_session
from database.models import User, Confession
from config import (
    MAX_CONFESSION_LENGTH, DAILY_CONFESSION_LIMIT,
    ERROR_MESSAGES, CONFESSION_CHANNEL, ADMIN_IDS
)
from .keyboards import (
    get_confession_keyboard, get_main_menu_keyboard,
    get_admin_keyboard
)
from .states import ConfessionStates
from .channel import post_confession

logger = logging.getLogger(__name__)

async def start_confession(message: types.Message, state: FSMContext):
    """Start the confession process."""
    try:
        with get_session() as session:
            user = session.query(User).filter_by(telegram_id=message.from_user.id).first()
            if not user:
                await message.answer(ERROR_MESSAGES['profile_required'])
                return

            # Check daily confession limit
            today = datetime.utcnow().date()
            confessions_today = session.query(Confession).filter(
                Confession.user_id == user.id,
                Confession.created_at >= today
            ).count()

            if confessions_today >= DAILY_CONFESSION_LIMIT:
                await message.answer(
                    f"You've reached your daily confession limit of {DAILY_CONFESSION_LIMIT}. "
                    "Please try again tomorrow!"
                )
                return

            await message.answer(
                f"Write your confession (max {MAX_CONFESSION_LENGTH} characters).\n"
                "Your identity will remain anonymous."
            )
            await state.set_state(ConfessionStates.waiting_for_confession)
    except Exception as e:
        logger.error(f"Error in start_confession: {e}")
        await message.answer(ERROR_MESSAGES['database_error'])
        await state.clear()

async def process_confession(message: types.Message, state: FSMContext):
    """Process user's confession."""
    try:
        if len(message.text) > MAX_CONFESSION_LENGTH:
            await message.answer(ERROR_MESSAGES['confession_too_long'])
            return

        with get_session() as session:
            user = session.query(User).filter_by(telegram_id=message.from_user.id).first()
            if not user:
                await message.answer(ERROR_MESSAGES['profile_required'])
                return

            # Create confession
            confession = Confession(
                user_id=user.id,
                content=message.text,
                status='pending'
            )
            session.add(confession)

            # Notify admins
            for admin_id in ADMIN_IDS:
                try:
                    await message.bot.send_message(
                        chat_id=admin_id,
                        text=(
                            f"📝 New confession for moderation:\n\n"
                            f"{message.text}\n\n"
                            f"Confession ID: {confession.id}"
                        ),
                        reply_markup=get_admin_keyboard()
                    )
                except Exception as e:
                    logger.error(f"Error notifying admin {admin_id}: {e}")

            await message.answer(
                "✅ Your confession has been submitted and is pending moderation.",
                reply_markup=get_main_menu_keyboard()
            )
            await state.clear()
    except Exception as e:
        logger.error(f"Error in process_confession: {e}")
        await message.answer(ERROR_MESSAGES['database_error'])
        await state.clear()

async def view_confessions(message: types.Message):
    """View recent confessions."""
    try:
        with get_session() as session:
            # Get recent approved confessions
            confessions = session.query(Confession).filter(
                Confession.status == 'approved'
            ).order_by(Confession.created_at.desc()).limit(10).all()

            if not confessions:
                await message.answer("No confessions available at the moment.")
                return

            for confession in confessions:
                await message.answer(
                    f"💭 Confession #{confession.id}\n\n"
                    f"{confession.content}\n\n"
                    f"Posted: {confession.created_at.strftime('%Y-%m-%d %H:%M')}"
                )
    except Exception as e:
        logger.error(f"Error in view_confessions: {e}")
        await message.answer(ERROR_MESSAGES['database_error'])

async def view_my_confessions(message: types.Message):
    """View user's own confessions."""
    try:
        with get_session() as session:
            user = session.query(User).filter_by(telegram_id=message.from_user.id).first()
            if not user:
                await message.answer(ERROR_MESSAGES['profile_required'])
                return

            confessions = session.query(Confession).filter(
                Confession.user_id == user.id
            ).order_by(Confession.created_at.desc()).all()

            if not confessions:
                await message.answer("You haven't submitted any confessions yet.")
                return

            for confession in confessions:
                status_emoji = {
                    'pending': '⏳',
                    'approved': '✅',
                    'rejected': '❌'
                }.get(confession.status, '❓')

                await message.answer(
                    f"{status_emoji} Confession #{confession.id}\n\n"
                    f"{confession.content}\n\n"
                    f"Status: {confession.status.title()}\n"
                    f"Posted: {confession.created_at.strftime('%Y-%m-%d %H:%M')}"
                )
    except Exception as e:
        logger.error(f"Error in view_my_confessions: {e}")
        await message.answer(ERROR_MESSAGES['database_error'])

async def cancel_confession(message: types.Message, state: FSMContext):
    """Cancel the confession process."""
    try:
        await message.answer(
            "Confession cancelled.",
            reply_markup=get_main_menu_keyboard()
        )
        await state.clear()
    except Exception as e:
        logger.error(f"Error in cancel_confession: {e}")
        await message.answer(ERROR_MESSAGES['database_error'])
        await state.clear()

async def moderate_confession(callback: types.CallbackQuery, state: FSMContext):
    """Moderate a confession (admin only)."""
    try:
        if callback.from_user.id not in ADMIN_IDS:
            await callback.answer("You don't have permission to moderate confessions.")
            return

        action, confession_id = callback.data.split(':')
        confession_id = int(confession_id)

        with get_session() as session:
            confession = session.query(Confession).get(confession_id)
            if not confession:
                await callback.answer("Confession not found!")
                return

            if action == 'approve':
                confession.status = 'approved'
                # Post to confession channel
                await post_confession(callback.bot, confession)
                # Notify user
                user = session.query(User).get(confession.user_id)
                if user:
                    await callback.bot.send_message(
                        chat_id=user.telegram_id,
                        text="✅ Your confession has been approved and posted!"
                    )
            else:  # reject
                confession.status = 'rejected'
                # Notify user
                user = session.query(User).get(confession.user_id)
                if user:
                    await callback.bot.send_message(
                        chat_id=user.telegram_id,
                        text="❌ Your confession has been rejected."
                    )

            await callback.answer(f"Confession {action}d successfully!")
    except Exception as e:
        logger.error(f"Error in moderate_confession: {e}")
        await callback.message.answer(ERROR_MESSAGES['database_error'])

def register_confession_handlers(dp):
    """Register all confession-related handlers."""
    dp.message.register(start_confession, Command("confess"))
    dp.message.register(process_confession, ConfessionStates.waiting_for_confession)
    dp.message.register(view_confessions, Command("confessions"))
    dp.message.register(view_my_confessions, Command("myconfessions"))
    dp.message.register(cancel_confession, Command("cancel"), ConfessionStates.waiting_for_confession)
    dp.callback_query.register(moderate_confession, F.data.startswith(("approve:", "reject:"))) 