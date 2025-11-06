"""Callback query handlers"""
from aiogram import Router
from aiogram.types import CallbackQuery
from loguru import logger

from data.database import Database
from bot.keyboards.main import get_confirm_clear_keyboard
from bot.keyboards.gender import get_gender_keyboard

router = Router()


@router.callback_query(lambda c: c.data in ["gender_male", "gender_female"])
async def callback_gender_selection(callback: CallbackQuery, db: Database):
    """
    Handle gender selection.
    
    Args:
        callback: Callback query
        db: Database instance
    """
    user_id = callback.from_user.id
    gender = "male" if callback.data == "gender_male" else "female"
    
    # Save gender preference
    await db.set_assistant_gender(user_id, gender)
    
    logger.info(f"User {user_id} selected assistant gender: {gender}")
    
    from bot.keyboards.reply import get_main_menu_keyboard
    
    # Разные приветствия для разных полов
    if gender == "male":
        greeting = "Привет, Сергей на связи! Что интересует по нашей продукции?"
    else:
        greeting = "Привет, я Екатерина 💙 Чем могу помочь?"
    
    await callback.message.edit_text(greeting)
    
    # Send menu keyboard
    await callback.message.answer(
        "Меню управления всегда доступно на панели ниже 👇",
        reply_markup=get_main_menu_keyboard()
    )
    
    await callback.answer()


@router.callback_query(lambda c: c.data == "change_gender")
async def callback_change_gender(callback: CallbackQuery):
    """
    Handle change gender request.
    
    Args:
        callback: Callback query
    """
    await callback.message.edit_text(
        "**Выберите, с кем вам удобнее общаться:**",
        reply_markup=get_gender_keyboard()
    )
    await callback.answer()


@router.callback_query(lambda c: c.data == "clear_history")
async def callback_clear_history(callback: CallbackQuery):
    """
    Handle clear history button.
    
    Args:
        callback: Callback query
    """
    await callback.message.edit_text(
        "🗑 Вы уверены, что хотите очистить историю переписки?\n\n"
        "⚠️ Это действие нельзя отменить.",
        reply_markup=get_confirm_clear_keyboard()
    )
    await callback.answer()


@router.callback_query(lambda c: c.data == "confirm_clear")
async def callback_confirm_clear(callback: CallbackQuery, db: Database):
    """
    Handle confirmation of clearing history.
    
    Args:
        callback: Callback query
        db: Database instance
    """
    user_id = callback.from_user.id
    
    try:
        # Clear history from database
        deleted_count = await db.clear_history(user_id)
        
        logger.info(f"Cleared history for user {user_id}: {deleted_count} messages deleted")
        
        await callback.message.edit_text(
            f"✅ История диалога очищена!\n\n"
            f"Удалено сообщений из памяти: {deleted_count}\n\n"
            "💡 *Примечание:* Сообщения в чате остаются видимыми. "
            "Чтобы очистить чат, используйте стандартную функцию Telegram "
            "(нажмите на название бота → Очистить историю).\n\n"
            "Теперь можете начать новый диалог 💬"
        )
    
    except Exception as e:
        logger.error(f"Error clearing history for user {user_id}: {e}")
        await callback.message.edit_text(
            "😔 Произошла ошибка при очистке истории. Попробуйте позже."
        )
    
    await callback.answer()


@router.callback_query(lambda c: c.data == "cancel_clear")
async def callback_cancel_clear(callback: CallbackQuery):
    """
    Handle cancellation of clearing history.
    
    Args:
        callback: Callback query
    """
    await callback.message.edit_text(
        "❌ Очистка отменена.\n\n"
        "История переписки сохранена.\n\n"
        "Используйте /menu для вызова меню."
    )
    await callback.answer("Отменено")

