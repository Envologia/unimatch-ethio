from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from typing import Callable, Dict, Any, Awaitable
import logging

logger = logging.getLogger(__name__)

class RateLimitMiddleware(BaseMiddleware):
    """Simple pass-through middleware."""
    
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        """Pass through the request to the handler."""
        try:
            return await handler(event, data)
        except Exception as e:
            logger.error(f"Error in middleware: {e}")
            raise

    async def close(self):
        """Clean up middleware resources."""
        pass 