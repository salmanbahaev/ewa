"""Product search in catalog"""
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
    Search products in catalog by keywords with expanded search.
    
    Args:
        query: Search query (keywords, symptoms, goals)
        max_results: Maximum number of results to return
        
    Returns:
        List of matching products
    """
    catalog = load_json_file(config.CATALOG_PATH)
    if not catalog:
        return []
    
    query_lower = query.lower()
    query_words = set(query_lower.split())
    
    # Расширенный поиск - синонимы и связанные темы
    synonyms = {
        "мужская сила": ["тестостерон", "либидо", "потенция", "мужское здоровье", "для него"],
        "мужской": ["тестостерон", "либидо", "для него", "мужское"],
        "потенция": ["тестостерон", "либидо", "мужская сила"],
        "память": ["мозг", "концентрация", "когнитивные", "обучаемость"],
        "сон": ["успокоение", "релакс", "отдых"],
        "кожа": ["лицо", "уход", "красота"],
        "волосы": ["уход", "красота"],
        "иммунитет": ["защита", "здоровье", "витамин с"],
    }
    
    # Добавляем синонимы к поиску
    expanded_words = query_words.copy()
    for word in query_words:
        for key, values in synonyms.items():
            if word in key or key in word:
                expanded_words.update(values)
    
    results = []
    
    for product in catalog:
        score = 0
        
        # Search in tags (highest priority)
        if product.get("tags"):
            for tag in product["tags"]:
                tag_lower = tag.lower()
                # Exact match in tags
                if tag_lower in query_lower or query_lower in tag_lower:
                    score += 5
                # Word match in tags (including expanded)
                elif any(word in tag_lower for word in expanded_words):
                    score += 3
        
        # Search in name
        name_lower = product.get("name", "").lower()
        if query_lower in name_lower:
            score += 4
        elif any(word in name_lower for word in expanded_words):
            score += 2
        
        # Search in description
        description_lower = product.get("description", "").lower()
        if query_lower in description_lower:
            score += 3
        elif any(word in description_lower for word in expanded_words):
            score += 1
        
        # Search in category
        category_lower = product.get("category", "").lower()
        if query_lower in category_lower:
            score += 2
        
        # Search in subcategory
        if product.get("subcategory"):
            subcategory_lower = product["subcategory"].lower()
            if query_lower in subcategory_lower:
                score += 2
        
        if score > 0:
            results.append({
                "product": product,
                "score": score
            })
    
    # Sort by score (descending)
    results.sort(key=lambda x: x["score"], reverse=True)
    
    # Return top results
    top_results = results[:max_results]
    
    logger.info(f"Found {len(results)} products for query '{query}', returning top {len(top_results)}")
    
    return [item["product"] for item in top_results]


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


def format_product_for_gpt(product: Dict) -> str:
    """
    Format product data for GPT context.
    
    Args:
        product: Product dictionary
        
    Returns:
        Formatted string
    """
    parts = [
        f"🏷 **{product.get('name', 'Неизвестно')}**",
        f"Категория: {product.get('category', 'Не указана')}",
    ]
    
    if product.get('subcategory'):
        parts.append(f"Подкатегория: {product['subcategory']}")
    
    parts.append(f"💰 Цена: {product.get('price_rub', 'Уточняйте')} руб.")
    parts.append(f"📦 Объем: {product.get('quantity_volume', 'Не указан')}")
    
    if product.get('description'):
        parts.append(f"📝 Описание: {product['description']}")
    
    if product.get('tags'):
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

