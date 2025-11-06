"""Clear history command handler"""
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from loguru import logger

from data.database import Database

router = Router()


@router.message(Command("clear"))
async def cmd_clear(message: Message, db: Database):
    """
    Handle /clear command - clears chat history from database.
    
    Args:
        message: Telegram message
        db: Database instance
    """
    user = message.from_user
    user_id = user.id
    
    logger.info(f"User {user_id} (@{user.username}) requested history clear")
    
    try:
        # Clear history from database
        deleted_count = await db.clear_history(user_id)
        
        logger.info(f"Cleared history for user {user_id}: {deleted_count} messages deleted")
        
        await message.answer(
            f"✅ **История диалога очищена!**\n\n"
            f"Удалено сообщений из памяти: {deleted_count}\n\n"
            "Теперь можем начать новый диалог с чистого листа 💬"
        )
    
    except Exception as e:
        logger.error(f"Error clearing history for user {user_id}: {e}")
        await message.answer(
            "😔 Произошла ошибка при очистке истории. Попробуйте позже."
        )

