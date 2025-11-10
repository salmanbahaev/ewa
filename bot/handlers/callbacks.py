"""Callback query handlers"""
from aiogram import Router, F
from aiogram.types import CallbackQuery
from loguru import logger

from data.database import Database
from ai.assistant import AIAssistant
from ai.product_search import search_products, format_products_list
from bot.keyboards.main import get_confirm_clear_keyboard
from bot.keyboards.gender import get_gender_keyboard
from bot.keyboards.product import get_products_list_keyboard

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
        greeting = """Здравствуйте! Меня зовут Сергей, я консультант EWA PRODUCT.

🛍 **EWA PRODUCT** - премиальные БАДы, нутрицевтики и косметика.

💡 **Что я могу:**
• Подобрать продукты под вашу задачу
• Рассказать о составе и применении
• Найти товары по категориям
• Ответить на вопросы о компании

**Примеры вопросов:**
"Что для суставов?" • "Покажи для похудения"
"Что для мозга и памяти?" • "Нужен коллаген"

Чем могу быть полезен?"""
    else:
        greeting = """Здравствуйте! Меня зовут Екатерина, я консультант EWA PRODUCT 😊

🛍 **EWA PRODUCT** - премиальные БАДы, нутрицевтики и косметика.

💡 **Что я могу:**
• Подобрать продукты под вашу задачу
• Рассказать о составе и применении
• Найти товары по категориям
• Ответить на вопросы о компании

**Примеры вопросов:**
"Что для суставов?" • "Покажи для похудения"
"Что для кожи лица?" • "Нужен коллаген"

Чем могу помочь?"""
    
    await callback.message.edit_text(greeting)
    
    # Send menu keyboard with hint
    await callback.message.answer(
        "Меню управления всегда доступно на панели ниже 👇\n\nПросто напишите ваш вопрос или задачу!",
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


@router.callback_query(F.data.startswith("back_to_list:"))
async def callback_back_to_list(callback: CallbackQuery, db: Database):
    """
    Return to product list from product card - just delete the card message
    """
    try:
        # Simply delete the product card message
        # This will make the product list message (above) become the last message again
        await callback.message.delete()
        await callback.answer()
        logger.info("Deleted product card, returned to product list")
        
    except Exception as e:
        logger.error(f"Error in callback_back_to_list: {e}")
        await callback.answer("❌ Произошла ошибка", show_alert=True)


@router.callback_query(F.data.startswith("more_products:"))
async def callback_more_products(callback: CallbackQuery, assistant: AIAssistant, db: Database):
    """
    Show more products (pagination).
    
    Triggered by: more_products:{query}:{offset}
    """
    try:
        # Parse callback data
        parts = callback.data.split(":", 2)
        query = parts[1]
        offset = int(parts[2])
        
        logger.info(f"Loading more products for '{query}', offset={offset}")
        
        # Search products again
        products = search_products(query, max_results=20)
        
        # Get next 3 products
        next_products = products[offset:offset + 3]
        
        if not next_products:
            await callback.answer("❌ Больше товаров нет", show_alert=True)
            return
        
        # Format response text with page indicator
        assistant_gender = await db.get_assistant_gender(callback.from_user.id)
        
        # Calculate page numbers
        start_num = offset + 1
        end_num = offset + len(next_products)
        total_products = len(products)
        
        if assistant_gender == "male":
            response_text = f"Товары {start_num}-{end_num} из {total_products}:\n\n"
        elif assistant_gender == "female":
            response_text = f"Товары {start_num}-{end_num} из {total_products} 😊\n\n"
        else:
            response_text = f"Товары {start_num}-{end_num} из {total_products}:\n\n"
        
        # Format products with real numbers
        for idx, product in enumerate(next_products):
            real_number = offset + idx + 1  # Real product number
            response_text += f"{real_number}. {product.get('name')}\n"
            
            # Show price (always show, even if 0 - will be fixed after catalog reparse)
            price = product.get('price_rub', 0)
            response_text += f"   - 💰 Цена: {price:,} ₽\n".replace(',', ' ')
            
            # Show volume only if it exists
            volume = product.get('quantity_volume')
            if volume:
                response_text += f"   - 📦 Объем: {volume}\n"
            
            # Short description from tags[0] (same as in GPT response)
            if product.get('tags') and len(product['tags']) > 0:
                short_desc = product['tags'][0]
                response_text += f"   - 📝 Описание: {short_desc}\n"
            
            response_text += "\n"
        
        # Create new keyboard with updated pagination
        keyboard = get_products_list_keyboard(
            products=next_products,
            total_found=len(products),
            current_offset=offset,
            query=query
        )
        
        # Edit current message instead of sending new one
        await callback.message.edit_text(
            response_text,
            reply_markup=keyboard
        )
        
        await callback.answer()
        logger.info(f"Showed products {offset+1}-{offset+len(next_products)} of {len(products)}")
        
    except Exception as e:
        logger.error(f"Error in callback_more_products: {e}")
        await callback.answer("❌ Произошла ошибка", show_alert=True)

