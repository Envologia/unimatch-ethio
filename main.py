import logging
import asyncio
import os
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config import BOT_TOKEN
from database.database import init_db
from handlers.profile import register_profile_handlers
from handlers.states import ProfileStates, EditProfileStates
from handlers.keyboards import get_main_menu_keyboard

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize bot and dispatcher
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

async def start_command(message):
    """Handle the /start command."""
    await message.answer(
        "Welcome to Uni Match Ethiopia! 🎓\n\n"
        "I can help you connect with other university students in Ethiopia.\n"
        "Use the menu below to get started:",
        reply_markup=get_main_menu_keyboard()
    )

async def error_handler(update, exception):
    """Handle errors gracefully."""
    logger.error(f"Update {update} caused error {exception}")
    if update and update.message:
        await update.message.answer(
            "Sorry, something went wrong. Please try again later."
        )

async def setup_bot():
    """Set up bot handlers and database."""
    try:
        # Initialize database
        init_db()
        logger.info("Database initialized successfully")

        # Register handlers
        dp.message.register(start_command, commands=["start"])
        register_profile_handlers(dp)
        
        # Register error handler
        dp.errors.register(error_handler)
        
        logger.info("Bot handlers registered successfully")
    except Exception as e:
        logger.error(f"Error setting up bot: {e}")
        raise

if __name__ == "__main__":
    try:
        asyncio.run(setup_bot())
        logger.info("Starting bot in polling mode...")
        asyncio.run(dp.start_polling(bot))
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped!")
    except Exception as e:
        logger.error(f"Unexpected error: {e}") 