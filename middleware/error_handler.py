import logging
import traceback
from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery
from aiogram.exceptions import (
    TelegramAPIError,
    TelegramBadRequest,
    TelegramNetworkError,
    TelegramRetryAfter,
    TelegramUnauthorizedError
)
from config import ERROR_MESSAGE

logger = logging.getLogger(__name__)

class ErrorHandlerMiddleware(BaseMiddleware):
    """Middleware for handling errors in request handlers."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        """Handle errors in request."""
        try:
            return await handler(event, data)
        except TelegramRetryAfter as e:
            # Handle rate limiting
            logger.warning(f"Rate limit exceeded: {e}")
            if isinstance(event, (Message, CallbackQuery)):
                await event.answer(
                    "Please wait a moment before trying again.",
                    show_alert=True
                )
        except TelegramBadRequest as e:
            # Handle invalid requests
            logger.error(f"Bad request: {e}")
            if isinstance(event, (Message, CallbackQuery)):
                await event.answer(
                    "Sorry, there was an error processing your request.",
                    show_alert=True
                )
        except TelegramUnauthorizedError as e:
            # Handle unauthorized access
            logger.error(f"Unauthorized: {e}")
            if isinstance(event, (Message, CallbackQuery)):
                await event.answer(
                    "Sorry, you are not authorized to perform this action.",
                    show_alert=True
                )
        except TelegramNetworkError as e:
            # Handle network errors
            logger.error(f"Network error: {e}")
            if isinstance(event, (Message, CallbackQuery)):
                await event.answer(
                    "Sorry, there was a network error. Please try again later.",
                    show_alert=True
                )
        except TelegramAPIError as e:
            # Handle other Telegram API errors
            logger.error(f"Telegram API error: {e}")
            if isinstance(event, (Message, CallbackQuery)):
                await event.answer(
                    "Sorry, there was an error with the Telegram API.",
                    show_alert=True
                )
        except Exception as e:
            # Handle unexpected errors
            logger.error(f"Unexpected error: {e}")
            logger.error(traceback.format_exc())
            if isinstance(event, (Message, CallbackQuery)):
                await event.answer(
                    "Sorry, an unexpected error occurred. Please try again later.",
                    show_alert=True
                )
            raise

    async def close(self) -> None:
        """Cleanup middleware resources."""
        pass

    async def _send_error_message(self, event: TelegramObject, error: str):
        """Send error message.
        
        Args:
            event: Telegram event
            error: Error message
        """
        try:
            if isinstance(event, Message):
                await event.answer(
                    ERROR_MESSAGE.format(error=error)
                )
            elif isinstance(event, CallbackQuery):
                await event.answer(
                    ERROR_MESSAGE.format(error=error),
                    show_alert=True
                )
        except Exception as e:
            logger.error(f"Error sending error message: {e}") 