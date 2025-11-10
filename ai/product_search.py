"""Product search in catalog - Semantic Search version"""
import json
from pathlib import Path
from typing import List, Dict, Optional
from loguru import logger
import config


def load_json_file(file_path: Path) -> any:
    """
    Load JSON file.
    
    Args:
        file_path: Path to JSON file
        
    Returns:
        Parsed JSON data
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading {file_path}: {e}")
        return None


def search_products(query: str, max_results: int = 5) -> List[Dict]:
    """
    Search products using semantic search.
    
    Args:
        query: Search query (keywords, symptoms, goals)
        max_results: Maximum number of results to return
        
    Returns:
        List of matching products sorted by relevance
    """
    from ai.embeddings import get_embeddings_search
    
    try:
        embeddings_search = get_embeddings_search()
        results = embeddings_search.search(query, max_results=max_results)
        
        logger.info(f"Found {len(results)} products for query '{query}'")
        return results
        
    except Exception as e:
        logger.error(f"Error in semantic search: {e}")
        # Fallback to returning empty list
        return []


def get_company_info(info_type: str, city: Optional[str] = None) -> Dict:
    """
    Get company information from JSON files.
    
    Args:
        info_type: Type of info (company, business, events, geography, all)
        city: City name for geography search (optional)
        
    Returns:
        Dictionary with requested information
    """
    result = {}
    
    if info_type in ["company", "all"]:
        company_data = load_json_file(config.COMPANY_PATH)
        if company_data:
            result["company"] = company_data
    
    if info_type in ["business", "all"]:
        business_data = load_json_file(config.BUSINESS_PATH)
        if business_data:
            result["business"] = business_data
    
    if info_type in ["events", "all"]:
        events_data = load_json_file(config.EVENTS_PATH)
        if events_data:
            result["events"] = events_data
    
    if info_type in ["geography", "all"]:
        geography_data = load_json_file(config.GEOGRAPHY_PATH)
        if geography_data:
            # Filter by city if provided
            if city and isinstance(geography_data, list):
                city_lower = city.lower()
                filtered = [
                    location for location in geography_data
                    if city_lower in location.get("city", "").lower()
                ]
                result["geography"] = filtered if filtered else geography_data
            else:
                result["geography"] = geography_data
    
    logger.info(f"Retrieved {info_type} info" + (f" for city {city}" if city else ""))
    
    return result


def format_product_for_gpt(product: Dict, short: bool = True) -> str:
    """
    Format product data for GPT context.
    
    Args:
        product: Product dictionary
        short: If True, use first tag as short description (for lists)
               If False, use full description (for product cards)
        
    Returns:
        Formatted string
    """
    parts = [
        f"🏷 **{product.get('name', 'Неизвестно')}**",
        f"Категория: {product.get('category', 'Не указана')}",
    ]
    
    if product.get('subcategory'):
        parts.append(f"Подкатегория: {product['subcategory']}")
    
    # Always show price
    price = product.get('price_rub', 0)
    parts.append(f"💰 Цена: {price} руб.")
    
    # Show volume only if it exists
    volume = product.get('quantity_volume')
    if volume:
        parts.append(f"📦 Объем: {volume}")
    
    # Use short description (first tag) for lists, full description for cards
    if short and product.get('tags') and len(product['tags']) > 0:
        # First tag is the short marketing description
        short_desc = product['tags'][0]
        parts.append(f"📝 Описание: {short_desc}")
    elif product.get('description'):
        parts.append(f"📝 Описание: {product['description']}")
    
    # Don't show all tags in short format (already using first tag as description)
    if not short and product.get('tags'):
        parts.append(f"🏷 Теги: {', '.join(product['tags'])}")
    
    return "\n".join(parts)


def format_products_list(products: List[Dict]) -> str:
    """
    Format list of products for GPT.
    
    Args:
        products: List of product dictionaries
        
    Returns:
        Formatted string with all products
    """
    if not products:
        return "Продукты не найдены."
    
    formatted = []
    for i, product in enumerate(products, 1):
        formatted.append(f"\n{i}. {format_product_for_gpt(product)}")
    
    return "\n".join(formatted)


def get_product_by_id(product_id: str) -> Optional[Dict]:
    """
    Get product by ID for displaying product card.
    
    Args:
        product_id: Product ID (e.g. "P003")
        
    Returns:
        Product dictionary or None if not found
    """
    catalog = load_json_file(config.CATALOG_PATH)
    if not catalog:
        return None
    
    for product in catalog:
        if product.get("id") == product_id:
            logger.info(f"Found product: {product.get('name')} ({product_id})")
            return product
    
    logger.warning(f"Product {product_id} not found")
    return None
