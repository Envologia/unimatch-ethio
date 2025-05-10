from aiogram import types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from datetime import datetime, timedelta
import random
import logging
from typing import Optional, List

from config import (
    DAILY_MATCH_LIMIT, MATCH_COOLDOWN_HOURS,
    ERROR_MESSAGES, MIN_AGE, MAX_AGE,
    MATCH_SCORE_WEIGHTS
)
from database.database import get_session
from database.models import User, Match, Gender
from .states import MatchStates
from .keyboards import (
    get_match_keyboard, get_unmatch_keyboard,
    get_main_menu_keyboard
)
from .channel import announce_match

logger = logging.getLogger(__name__)

async def start_matching(message: types.Message, state: FSMContext):
    """Start the matching process."""
    try:
        with get_session() as session:
            user = session.query(User).filter_by(telegram_id=message.from_user.id).first()
            if not user:
                await message.answer(ERROR_MESSAGES['profile_required'])
                return

            # Check daily match limit
            today = datetime.utcnow().date()
            matches_today = session.query(Match).filter(
                Match.user_id == user.id,
                Match.created_at >= today
            ).count()

            if matches_today >= DAILY_MATCH_LIMIT:
                await message.answer(
                    f"You've reached your daily match limit of {DAILY_MATCH_LIMIT}. "
                    "Please try again tomorrow!"
                )
                return

            # Get potential matches
            potential_matches = get_potential_matches(session, user)
            if not potential_matches:
                await message.answer(
                    "No potential matches found at the moment. Please try again later!"
                )
                return

            # Store matches in state
            await state.update_data(potential_matches=potential_matches)
            await state.set_state(MatchStates.viewing_matches)

            # Show first match
            await show_next_match(message, state)
    except Exception as e:
        logger.error(f"Error in start_matching: {e}")
        await message.answer(ERROR_MESSAGES['database_error'])
        await state.clear()

def get_potential_matches(session, user: User) -> List[User]:
    """Get potential matches for a user based on preferences and compatibility."""
    try:
        # Get users who haven't been matched with before
        excluded_users = session.query(Match.matched_user_id).filter(
            Match.user_id == user.id
        ).subquery()

        # Get users who haven't matched with the current user
        excluded_by = session.query(Match.user_id).filter(
            Match.matched_user_id == user.id
        ).subquery()

        # Base query for potential matches
        query = session.query(User).filter(
            User.id != user.id,
            User.id.notin_(excluded_users),
            User.id.notin_(excluded_by),
            User.gender != user.gender  # Match with opposite gender
        )

        # Apply filters based on preferences
        if user.preferred_age_min:
            query = query.filter(User.age >= user.preferred_age_min)
        if user.preferred_age_max:
            query = query.filter(User.age <= user.preferred_age_max)
        if user.preferred_university:
            query = query.filter(User.university == user.preferred_university)

        # Get all potential matches
        potential_matches = query.all()

        # Calculate match scores and sort
        scored_matches = []
        for match in potential_matches:
            score = calculate_match_score(user, match)
            scored_matches.append((match, score))

        # Sort by score in descending order
        scored_matches.sort(key=lambda x: x[1], reverse=True)

        # Return top matches
        return [match for match, _ in scored_matches[:10]]
    except Exception as e:
        logger.error(f"Error in get_potential_matches: {e}")
        return []

def calculate_match_score(user1: User, user2: User) -> float:
    """Calculate compatibility score between two users."""
    try:
        score = 0.0

        # Age compatibility
        age_diff = abs(user1.age - user2.age)
        if age_diff <= 2:
            score += MATCH_SCORE_WEIGHTS['age'] * 1.0
        elif age_diff <= 5:
            score += MATCH_SCORE_WEIGHTS['age'] * 0.7
        else:
            score += MATCH_SCORE_WEIGHTS['age'] * 0.3

        # University compatibility
        if user1.university == user2.university:
            score += MATCH_SCORE_WEIGHTS['university']

        # Bio similarity (simple word matching)
        if user1.bio and user2.bio:
            common_words = set(user1.bio.lower().split()) & set(user2.bio.lower().split())
            if common_words:
                score += MATCH_SCORE_WEIGHTS['bio'] * (len(common_words) / 10)

        # Hobbies similarity
        if user1.hobbies and user2.hobbies:
            common_hobbies = set(user1.hobbies.lower().split(',')) & set(user2.hobbies.lower().split(','))
            if common_hobbies:
                score += MATCH_SCORE_WEIGHTS['hobbies'] * (len(common_hobbies) / 5)

        return score
    except Exception as e:
        logger.error(f"Error in calculate_match_score: {e}")
        return 0.0

async def show_next_match(message: types.Message, state: FSMContext):
    """Show the next potential match."""
    try:
        data = await state.get_data()
        potential_matches = data.get('potential_matches', [])
        
        if not potential_matches:
            await message.answer(
                "No more potential matches found. Try again later!",
                reply_markup=get_main_menu_keyboard()
            )
            await state.clear()
            return

        # Get next match
        match = potential_matches.pop(0)
        await state.update_data(potential_matches=potential_matches)

        # Format match profile
        profile_text = format_match_profile(match)
        
        # Send match profile with photo
        if match.photo_id:
            await message.answer_photo(
                photo=match.photo_id,
                caption=profile_text,
                reply_markup=get_match_keyboard(match.id)
            )
        else:
            await message.answer(
                text=profile_text,
                reply_markup=get_match_keyboard(match.id)
            )
    except Exception as e:
        logger.error(f"Error in show_next_match: {e}")
        await message.answer(ERROR_MESSAGES['database_error'])
        await state.clear()

async def process_match_choice(callback: types.CallbackQuery, state: FSMContext):
    """Process user's choice (like/skip) for a match."""
    try:
        action, user_id = callback.data.split(':')
        user_id = int(user_id)

        with get_session() as session:
            current_user = session.query(User).filter_by(telegram_id=callback.from_user.id).first()
            if not current_user:
                await callback.message.answer(ERROR_MESSAGES['profile_required'])
                return

            if action == 'like':
                # Check if it's a mutual match
                existing_match = session.query(Match).filter(
                    Match.user_id == user_id,
                    Match.matched_user_id == current_user.id,
                    Match.status == 'liked'
                ).first()

                if existing_match:
                    # It's a mutual match!
                    existing_match.status = 'matched'
                    match = Match(
                        user_id=current_user.id,
                        matched_user_id=user_id,
                        status='matched'
                    )
                    session.add(match)

                    # Notify both users
                    await notify_mutual_match(callback.bot, current_user, user_id)
                    await announce_match(callback.bot, current_user, user_id)
                else:
                    # Create new match
                    match = Match(
                        user_id=current_user.id,
                        matched_user_id=user_id,
                        status='liked'
                    )
                    session.add(match)

                await callback.message.answer("❤️ You've liked this profile!")
            else:  # skip
                await callback.message.answer("⏭️ Skipped this profile.")

            # Show next match
            await show_next_match(callback.message, state)
            await callback.answer()
    except Exception as e:
        logger.error(f"Error in process_match_choice: {e}")
        await callback.message.answer(ERROR_MESSAGES['database_error'])
        await state.clear()

async def notify_mutual_match(bot, user: User, matched_user_id: int):
    """Notify users of a mutual match."""
    try:
        with get_session() as session:
            matched_user = session.query(User).get(matched_user_id)
            if not matched_user:
                return

            # Notify first user
            await bot.send_message(
                chat_id=user.telegram_id,
                text=f"🎉 It's a match! You and {matched_user.first_name} have liked each other!",
                reply_markup=get_unmatch_keyboard(matched_user_id)
            )

            # Notify second user
            await bot.send_message(
                chat_id=matched_user.telegram_id,
                text=f"🎉 It's a match! You and {user.first_name} have liked each other!",
                reply_markup=get_unmatch_keyboard(user.id)
            )
    except Exception as e:
        logger.error(f"Error in notify_mutual_match: {e}")

async def process_unmatch(callback: types.CallbackQuery):
    """Process unmatch request."""
    try:
        user_id = int(callback.data.split(':')[1])
        
        with get_session() as session:
            # Update both match records
            session.query(Match).filter(
                (Match.user_id == callback.from_user.id) & (Match.matched_user_id == user_id) |
                (Match.user_id == user_id) & (Match.matched_user_id == callback.from_user.id)
            ).update({'status': 'unmatched'})

            await callback.message.answer(
                "You've unmatched with this user.",
                reply_markup=get_main_menu_keyboard()
            )
            await callback.answer()
    except Exception as e:
        logger.error(f"Error in process_unmatch: {e}")
        await callback.message.answer(ERROR_MESSAGES['database_error'])

def format_match_profile(user: User) -> str:
    """Format user profile for matching display."""
    return (
        f"👤 Potential Match\n\n"
        f"Name: {user.first_name} {user.last_name or ''}\n"
        f"Age: {user.age}\n"
        f"University: {user.university}\n"
        f"Bio: {user.bio}\n"
        f"Hobbies: {user.hobbies}"
    )

def register_match_handlers(dp):
    """Register all match-related handlers."""
    dp.message.register(start_matching, Command("match"))
    dp.callback_query.register(process_match_choice, F.data.startswith(("like:", "skip:")), MatchStates.viewing_matches)
    dp.callback_query.register(process_unmatch, F.data.startswith("unmatch:")) 