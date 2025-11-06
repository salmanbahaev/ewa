"""Handlers for reply keyboard menu buttons"""
from aiogram import Router, F
from aiogram.types import Message
from loguru import logger

from data.database import Database
from bot.keyboards.gender import get_gender_keyboard

router = Router()


@router.message(F.text == "🔄 Сменить ассистента")
async def handle_change_assistant(message: Message):
    """
    Handle change assistant button from reply keyboard.
    
    Args:
        message: Telegram message
    """
    user = message.from_user
    logger.info(f"User {user.id} wants to change assistant")
    
    await message.answer(
        "**Выберите, с кем вам удобнее общаться:**",
        reply_markup=get_gender_keyboard()
    )


@router.message(F.text == "🗑 Очистить историю")
async def handle_clear_history(message: Message, db: Database):
    """
    Handle clear history button from reply keyboard.
    
    Args:
        message: Telegram message
        db: Database instance
    """
    user_id = message.from_user.id
    
    try:
        deleted_count = await db.clear_history(user_id)
        logger.info(f"Cleared history for user {user_id}: {deleted_count} messages")
        
        await message.answer(
            f"✅ История очищена!\n\n"
            f"Удалено сообщений: {deleted_count}\n\n"
            "Можем начать заново 💬"
        )
    except Exception as e:
        logger.error(f"Error clearing history: {e}")
        await message.answer("😔 Произошла ошибка. Попробуй позже.")

