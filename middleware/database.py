import logging
from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_session

logger = logging.getLogger(__name__)

class DatabaseMiddleware(BaseMiddleware):
    """Middleware for handling database sessions."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        """Handle database session for request."""
        try:
            # Get database session
            async for session in get_session():
                # Add session to data
                data["session"] = session

                # Call handler with session
                return await handler(event, data)
        except Exception as e:
            logger.error(f"Database middleware error: {e}")
            raise
        finally:
            # Ensure session is closed
            if "session" in data:
                await data["session"].close()

    async def close(self) -> None:
        """Cleanup middleware resources."""
        try:
            # Close any remaining sessions
            if hasattr(self, "_session"):
                await self._session.close()
        except Exception as e:
            logger.error(f"Error closing database middleware: {e}")
            raise 