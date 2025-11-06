"""Menu command handler"""
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from loguru import logger

from bot.keyboards.main import get_main_keyboard

router = Router()


@router.message(Command("menu"))
async def cmd_menu(message: Message):
    """
    Handle /menu command.
    
    Args:
        message: Telegram message
    """
    user = message.from_user
    logger.info(f"User {user.id} (@{user.username}) opened menu")
    
    menu_text = """⚙️ **Меню управления**

Выберите действие:"""
    
    await message.answer(
        menu_text,
        reply_markup=get_main_keyboard()
    )

