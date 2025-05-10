import asyncio
import logging
import sys
from typing import Dict, Any, Callable, Awaitable, Union

from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Update, Message
from aiogram.utils.exceptions import TelegramAPIError

from config import (
    BOT_TOKEN, REDIS_URL, LOG_LEVEL, LOG_FORMAT,
    LOG_DATE_FORMAT, ENABLE_MATCHING, ENABLE_CONFESSIONS,
    ENABLE_REPORTS, ENABLE_CHANNEL_POSTS,
    BOT_USERNAME, WEBHOOK_URL, WEBHOOK_PATH,
    MESSAGES, ERROR_MESSAGES, LOG_FILE
)
from database.database import init_db, close_db, get_session
from database.models import User
from handlers import (
    profile, match, confession, channel, report,
    states, keyboards,
    register_user_handlers,
    register_confession_handlers,
    register_channel_handlers,
    register_admin_handlers
)
from handlers.profile import register_profile_handlers
from handlers.confession import register_confession_handlers
from handlers.channel import register_channel_handlers, check_channel_membership
from handlers.match import register_match_handlers
from handlers.states import (
    ProfileStates, EditProfileStates, ConfessionStates,
    ChannelStates, MatchStates
)
from handlers.keyboards import get_main_menu_keyboard
from middleware import (
    DatabaseMiddleware, RateLimitMiddleware, ErrorHandlingMiddleware
)
from middleware.database import DatabaseMiddleware
from middleware.error_handler import ErrorHandlerMiddleware

# Configure logging
logging.basicConfig(
    level=LOG_LEVEL,
    format=LOG_FORMAT,
    datefmt=LOG_DATE_FORMAT,
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

async def setup_commands() -> None:
    """Set up bot commands."""
    commands = [
        types.BotCommand(command="start", description="Start the bot"),
        types.BotCommand(command="help", description="Show help message"),
        types.BotCommand(command="verify", description="Verify channel membership"),
        types.BotCommand(command="match", description="Start matching"),
        types.BotCommand(command="confess", description="Send a confession"),
        types.BotCommand(command="profile", description="View your profile"),
        types.BotCommand(command="settings", description="Change settings")
    ]
    await bot.set_my_commands(commands)

async def setup_middleware() -> None:
    """Set up middleware."""
    dp.update.middleware(DatabaseMiddleware())
    dp.update.middleware(ErrorHandlerMiddleware())

async def setup_handlers() -> None:
    """Set up all handlers."""
    register_user_handlers(dp)
    register_match_handlers(dp)
    register_confession_handlers(dp)
    register_channel_handlers(dp)
    register_admin_handlers(dp)

async def setup_bot(dp: Dispatcher, db: Database):
    """Setup bot.
    
    Args:
        dp: Dispatcher instance
        db: Database instance
    """
    try:
        # Setup commands
        await setup_commands()

        # Setup middleware
        await setup_middleware()

        # Setup handlers
        await setup_handlers()

        logger.info("Bot setup completed successfully")

    except Exception as e:
        logger.error(f"Error setting up bot: {e}")
        raise

async def start_command(message: Message) -> None:
    """Handle /start command."""
    try:
        with get_session() as session:
            user = session.query(User).get(message.from_user.id)
            if not user:
                user = User(
                    id=message.from_user.id,
                    username=message.from_user.username,
                    first_name=message.from_user.first_name,
                    last_name=message.from_user.last_name,
                    created_at=message.date
                )
                session.add(user)
                session.commit()
                await message.answer(MESSAGES['welcome_new'])
            else:
                await message.answer(MESSAGES['welcome_back'])
    except Exception as e:
        logger.error(f"Error in start_command: {e}")
        await message.answer(ERROR_MESSAGES['database_error'])

async def help_command(message: Message) -> None:
    """Handle /help command."""
    try:
        await message.answer(MESSAGES['help'])
    except Exception as e:
        logger.error(f"Error in help_command: {e}")
        await message.answer(ERROR_MESSAGES['database_error'])

async def error_handler(update: Update, exception: Exception) -> None:
    """Handle errors."""
    try:
        if isinstance(exception, TelegramAPIError):
            logger.error(f"Telegram API Error: {exception}")
            if update.message:
                await update.message.answer(ERROR_MESSAGES['telegram_error'])
        else:
            logger.error(f"Unexpected error: {exception}")
            if update.message:
                await update.message.answer(ERROR_MESSAGES['unexpected_error'])
    except Exception as e:
        logger.error(f"Error in error_handler: {e}")

async def main() -> None:
    """Main function."""
    try:
        # Initialize database
        await init_db()
        
        # Set up bot
        await setup_commands()
        await setup_middleware()
        await setup_handlers()
        
        # Register error handler
        dp.errors.register(error_handler)
        
        # Start polling
        logger.info("Starting bot...")
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Error in main: {e}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        # Run the bot
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped!")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        close_db() 