"""Product card handler - displays product details with photo"""
from aiogram import Router, F
from aiogram.types import CallbackQuery, InputMediaPhoto, FSInputFile
from loguru import logger
import tempfile
import requests
from pathlib import Path

from ai.product_search import get_product_by_id
from bot.keyboards.product import get_product_card_keyboard


router = Router()


def format_product_card_caption(product: dict) -> str:
    """
    Format product information for card caption.
    
    Args:
        product: Product dictionary
        
    Returns:
        Formatted caption text
    """
    parts = []
    
    # Название
    parts.append(f"🏷 <b>{product.get('name', 'Товар')}</b>\n")
    
    # Категория
    category = product.get('category', '')
    if category:
        parts.append(f"📂 {category}")
    
    # Цена
    price = product.get('price_rub', 0)
    if price:
        parts.append(f"💰 <b>{price:,} ₽</b>".replace(',', ' '))
    
    # Объем/упаковка
    volume = product.get('quantity_volume')
    if volume:
        parts.append(f"📦 {volume}")
    
    # Полное описание с форматированием
    description = product.get('description', '')
    if description:
        # Заменяем маркеры списка на эмодзи для лучшей читаемости
        formatted_desc = description.replace('• ', '\n✓ ')
        parts.append(f"\n📝 <b>Описание:</b>\n{formatted_desc}")
    
    return "\n".join(parts)


async def download_image(url: str) -> Path:
    """
    Download product image to temporary file.
    
    Args:
        url: Image URL
        
    Returns:
        Path to downloaded file
    """
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    
    # Create temp file
    suffix = Path(url).suffix or ".jpg"
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    temp_file.write(response.content)
    temp_file.close()
    
    return Path(temp_file.name)


@router.callback_query(F.data.startswith("product:"))
async def show_product_card(callback: CallbackQuery):
    """
    Show product card with photo and full details.
    
    Triggered by: product:{product_id}:{query}:{offset} callback
    """
    try:
        # Extract product_id, query, and offset from callback data
        parts = callback.data.split(":", 3)
        product_id = parts[1]
        query = parts[2] if len(parts) > 2 else ""
        offset = int(parts[3]) if len(parts) > 3 else 0
        
        logger.info(f"Showing product card for {product_id} to user {callback.from_user.id}")
        
        # Get product from catalog
        product = get_product_by_id(product_id)
        
        if not product:
            await callback.answer("❌ Товар не найден", show_alert=True)
            return
        
        # Get product details
        image_url = product.get("image")
        product_url = product.get("url")
        
        # Format caption
        caption = format_product_card_caption(product)
        keyboard = get_product_card_keyboard(product_url, query, offset)
        
        # Send product card as NEW message (with photo if available)
        if image_url:
            try:
                temp_image = await download_image(image_url)
                
                # Send photo with full product info
                photo = FSInputFile(temp_image)
                await callback.message.answer_photo(
                    photo=photo,
                    caption=caption,
                    parse_mode="HTML",
                    reply_markup=keyboard
                )
                
                # Clean up temp file
                temp_image.unlink(missing_ok=True)
                
            except Exception as e:
                logger.error(f"Error downloading/sending image: {e}")
                # Fallback - send as text message
                await callback.message.answer(
                    caption + "\n\n⚠️ (Изображение временно недоступно)",
                    parse_mode="HTML",
                    reply_markup=keyboard
                )
        else:
            # No image - send as text message
            await callback.message.answer(
                caption,
                parse_mode="HTML",
                reply_markup=keyboard
            )
        
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in show_product_card: {e}")
        await callback.answer("❌ Произошла ошибка", show_alert=True)

