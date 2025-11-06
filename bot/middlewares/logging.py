"""Logging middleware"""
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from loguru import logger


class LoggingMiddleware(BaseMiddleware):
    """Middleware for logging all bot interactions"""
    
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        """
        Log incoming events.
        
        Args:
            handler: Next handler
            event: Incoming event (Message or CallbackQuery)
            data: Handler data
            
        Returns:
            Handler result
        """
        # Log message
        if isinstance(event, Message):
            user = event.from_user
            logger.info(
                f"📨 Message | User: {user.id} (@{user.username}) | "
                f"Text: {event.text[:100] if event.text else 'No text'}"
            )
        
        # Log callback
        elif isinstance(event, CallbackQuery):
            user = event.from_user
            logger.info(
                f"🔘 Callback | User: {user.id} (@{user.username}) | "
                f"Data: {event.data}"
            )
        
        # Call next handler
        try:
            return await handler(event, data)
        except Exception as e:
            logger.error(f"Error in handler: {e}", exc_info=True)
            raise

