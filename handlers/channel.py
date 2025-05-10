from aiogram import types, F, Bot, Dispatcher
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from datetime import datetime
import logging
from typing import Optional, Union, Dict, Any, Callable, Awaitable

from config import (
    OFFICIAL_CHANNEL, CONFESSION_CHANNEL, ERROR_MESSAGES, 
    ADMIN_IDS, MESSAGES
)
from database.database import get_session
from database.models import User, Match, Confession
from .keyboards import (
    get_verification_keyboard, get_main_menu_keyboard,
    get_admin_keyboard
)
from .states import ChannelStates

logger = logging.getLogger(__name__)

async def check_channel_membership(message: Message) -> bool:
    """Check if user is a member of required channels."""
    try:
        # Check official channel membership
        try:
            official_member = await message.bot.get_chat_member(
                chat_id=OFFICIAL_CHANNEL,
                user_id=message.from_user.id
            )
            if official_member.status in ['left', 'kicked']:
                await message.answer(
                    "Please join our official channel first:",
                    reply_markup=get_verification_keyboard()
                )
                return False
        except Exception as e:
            logger.error(f"Error checking official channel membership: {e}")
            await message.answer(
                ERROR_MESSAGES['channel_error'],
                reply_markup=get_verification_keyboard()
            )
            return False

        # Check confession channel membership
        try:
            confession_member = await message.bot.get_chat_member(
                chat_id=CONFESSION_CHANNEL,
                user_id=message.from_user.id
            )
            if confession_member.status in ['left', 'kicked']:
                await message.answer(
                    "Please join our confession channel first:",
                    reply_markup=get_verification_keyboard()
                )
                return False
        except Exception as e:
            logger.error(f"Error checking confession channel membership: {e}")
            await message.answer(
                ERROR_MESSAGES['channel_error'],
                reply_markup=get_verification_keyboard()
            )
            return False

        return True
    except Exception as e:
        logger.error(f"Error in check_channel_membership: {e}")
        await message.answer(
            ERROR_MESSAGES['channel_error'],
            reply_markup=get_verification_keyboard()
        )
        return False

async def verify_membership(message: Message) -> None:
    """Verify user's channel membership."""
    try:
        if await check_channel_membership(message):
            await message.answer(
                "✅ You are a member of all required channels!",
                reply_markup=get_main_menu_keyboard()
            )
        else:
            await message.answer(
                "Please join our official channels to continue:",
                reply_markup=get_verification_keyboard()
            )
    except Exception as e:
        logger.error(f"Error in verify_membership: {e}")
        await message.answer(ERROR_MESSAGES['channel_error'])

async def start_channel_post(message: Message, state: FSMContext) -> None:
    """Start the channel post process (admin only)."""
    try:
        if message.from_user.id not in ADMIN_IDS:
            await message.answer(ERROR_MESSAGES['permission_error'])
            return

        await message.answer(
            "Send the content you want to post to the official channel.\n"
            "You can send text, photo, or video.\n"
            "Type /cancel to cancel."
        )
        await state.set_state(ChannelStates.waiting_for_post)
    except Exception as e:
        logger.error(f"Error in start_channel_post: {e}")
        await message.answer(ERROR_MESSAGES['database_error'])
        await state.clear()

async def process_channel_post(message: Message, state: FSMContext) -> None:
    """Process and post content to the official channel."""
    try:
        if message.from_user.id not in ADMIN_IDS:
            await message.answer(ERROR_MESSAGES['permission_error'])
            return

        if message.text:
            await message.bot.send_message(
                chat_id=OFFICIAL_CHANNEL,
                text=message.text
            )
        elif message.photo:
            await message.bot.send_photo(
                chat_id=OFFICIAL_CHANNEL,
                photo=message.photo[-1].file_id,
                caption=message.caption
            )
        elif message.video:
            await message.bot.send_video(
                chat_id=OFFICIAL_CHANNEL,
                video=message.video.file_id,
                caption=message.caption
            )
        else:
            await message.answer("Unsupported message type. Please send text, photo, or video.")
            return

        await message.answer(
            "✅ Content posted successfully!",
            reply_markup=get_admin_keyboard()
        )
        await state.clear()
    except Exception as e:
        logger.error(f"Error in process_channel_post: {e}")
        await message.answer(ERROR_MESSAGES['database_error'])
        await state.clear()

async def cancel_channel_post(message: Message, state: FSMContext) -> None:
    """Cancel the channel post process."""
    try:
        await message.answer(
            "Channel post cancelled.",
            reply_markup=get_admin_keyboard()
        )
        await state.clear()
    except Exception as e:
        logger.error(f"Error in cancel_channel_post: {e}")
        await message.answer(ERROR_MESSAGES['database_error'])
        await state.clear()

async def post_confession(bot: Bot, confession: Confession) -> None:
    """Post a confession to the confession channel."""
    try:
        await bot.send_message(
            chat_id=CONFESSION_CHANNEL,
            text=(
                f"💭 New Confession #{confession.id}\n\n"
                f"{confession.content}\n\n"
                f"Posted: {confession.created_at.strftime('%Y-%m-%d %H:%M')}"
            )
        )
    except Exception as e:
        logger.error(f"Error posting confession: {e}")

async def announce_match(bot: Bot, user1: User, user2_id: int) -> None:
    """Announce a new match in the official channel."""
    try:
        with get_session() as session:
            user2 = session.query(User).get(user2_id)
            if not user2:
                return

            await bot.send_message(
                chat_id=OFFICIAL_CHANNEL,
                text=(
                    "💝 New Match!\n\n"
                    f"🎓 {user1.university}\n"
                    f"👥 {user1.first_name} + {user2.first_name}\n\n"
                    "Wishing you the best of luck! 💫"
                )
            )
    except Exception as e:
        logger.error(f"Error announcing match: {e}")

def register_channel_handlers(dp: Dispatcher) -> None:
    """Register all channel-related handlers."""
    dp.message.register(verify_membership, Command("verify"))
    dp.message.register(start_channel_post, Command("post"), F.from_user.id.in_(ADMIN_IDS))
    dp.message.register(process_channel_post, ChannelStates.waiting_for_post)
    dp.message.register(cancel_channel_post, Command("cancel"), ChannelStates.waiting_for_post) 