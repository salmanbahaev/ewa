"""Product keyboards for inline buttons"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List, Dict


def get_product_details_keyboard(product_id: str) -> InlineKeyboardMarkup:
    """
    Create keyboard with 'Details' button for a product.
    
    Args:
        product_id: Product ID (e.g. "P003")
        
    Returns:
        InlineKeyboardMarkup with details button
    """
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📦 Подробнее", callback_data=f"product:{product_id}")]
    ])
    return keyboard


def get_product_card_keyboard(product_url: str = None, query: str = "", offset: int = 0) -> InlineKeyboardMarkup:
    """
    Create keyboard for product card with 'Buy on website' and 'Back to list' buttons.
    
    Args:
        product_url: URL to product page on website (optional)
        query: Search query to return to list
        offset: Offset to return to list
        
    Returns:
        InlineKeyboardMarkup with buttons
    """
    buttons = []
    
    # Add "Buy on website" button if URL exists
    if product_url:
        buttons.append([InlineKeyboardButton(text="🛒 Купить на сайте", url=product_url)])
    
    # Add "Back to list" button if we have query (meaning we came from search)
    if query:
        buttons.append([
            InlineKeyboardButton(
                text="◀️ Назад к списку",
                callback_data=f"back_to_list:{query}:{offset}"
            )
        ])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def get_products_list_keyboard(
    products: List[Dict], 
    total_found: int = 0,
    current_offset: int = 0,
    query: str = ""
) -> InlineKeyboardMarkup:
    """
    Create keyboard with numbered buttons for products + pagination.
    
    Args:
        products: List of product dictionaries (up to 3)
        total_found: Total number of products found
        current_offset: Current offset in pagination
        query: Search query for pagination
        
    Returns:
        InlineKeyboardMarkup with numbered product buttons + "More" button
    """
    buttons = []
    
    # Show up to 3 products with numbers
    for idx, product in enumerate(products[:3]):
        product_id = product.get("id")
        product_name = product.get("name", "Товар")
        
        # Truncate long names
        if len(product_name) > 30:
            product_name = product_name[:27] + "..."
        
        # Real product number based on offset
        real_number = current_offset + idx + 1
        
        # Include query and offset in callback for back navigation
        buttons.append([
            InlineKeyboardButton(
                text=f"{real_number}. {product_name}",
                callback_data=f"product:{product_id}:{query}:{current_offset}"
            )
        ])
    
    # Add pagination buttons (Back / Forward)
    pagination_row = []
    
    # Add "Back" button if not on first page
    if current_offset > 0:
        prev_offset = max(0, current_offset - 3)
        pagination_row.append(
            InlineKeyboardButton(
                text="◀️ Назад",
                callback_data=f"more_products:{query}:{prev_offset}"
            )
        )
    
    # Add "Forward" button if there are more products
    next_offset = current_offset + 3
    if total_found > next_offset:
        # На первой странице - "Еще товары", на остальных - "Вперёд"
        forward_text = "Еще товары ➡️" if current_offset == 0 else "Вперёд ➡️"
        pagination_row.append(
            InlineKeyboardButton(
                text=forward_text,
                callback_data=f"more_products:{query}:{next_offset}"
            )
        )
    
    # Add pagination row if any buttons exist
    if pagination_row:
        buttons.append(pagination_row)
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

