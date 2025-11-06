"""Bot keyboards"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_main_keyboard() -> InlineKeyboardMarkup:
    """
    Get main keyboard with actions.
    
    Returns:
        InlineKeyboardMarkup with buttons
    """
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🔄 Сменить ассистента",
                callback_data="change_gender"
            )
        ],
        [
            InlineKeyboardButton(
                text="🗑 Очистить историю",
                callback_data="clear_history"
            )
        ]
    ])
    return keyboard


def get_confirm_clear_keyboard() -> InlineKeyboardMarkup:
    """
    Get confirmation keyboard for clearing history.
    
    Returns:
        InlineKeyboardMarkup with Yes/No buttons
    """
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="✅ Да, очистить",
                callback_data="confirm_clear"
            ),
            InlineKeyboardButton(
                text="❌ Отмена",
                callback_data="cancel_clear"
            )
        ]
    ])
    return keyboard

