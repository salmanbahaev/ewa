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
        # Мозг и когнитивные функции
        "память": ["мозг", "концентрация", "когнитивные", "обучаемость", "brainstorm", "iq booster", "умственная деятельность", "активатор мозга"],
        "мозг": ["brainstorm", "iq booster", "память", "концентрация", "когнитивные", "умственная деятельность"],
        "концентрация": ["мозг", "brainstorm", "iq booster", "фокус", "внимание"],
        
        # Энергия и тонус
        "энергия": ["tone", "тонус", "бодрость", "активность", "сила", "заряд"],
        "тонус": ["tone", "энергия", "бодрость", "активность"],
        "усталость": ["tone", "энергия", "тонус", "бодрость"],
        
        # Стресс и сон
        "стресс": ["no stress", "ноустресс", "антистресс", "happy", "хэппи"],
        "сон": ["успокоение", "отдых", "no stress", "спокойствие"],
        "нервы": ["no stress", "стресс", "антистресс"],
        
        # Мужское и женское здоровье
        "мужская сила": ["тестостерон", "потенция", "мужское здоровье", "для него", "flame man", "stimul", "стимул"],
        "мужской": ["тестостерон", "для него", "мужское", "flame man", "stimul", "мужской фламе"],
        "потенция": ["тестостерон", "мужская сила", "flame man", "stimul"],
        "либидо": ["flame", "секс", "сексуальная энергия"],
        "женское": ["flame woman", "harmony", "женская гармония", "для нее", "женский фламе"],
        
        # Суставы и движение
        "суставы": ["flex", "флекс", "связки", "хрящи", "подвижность", "гибкость", "движение", "коллаген", "collagen", "hondroskin"],
        "суставов": ["flex", "флекс", "связки", "хрящи", "подвижность", "гибкость", "движение", "коллаген", "collagen", "hondroskin"],
        "гибкость": ["flex", "суставы", "подвижность", "движение"],
        "связки": ["flex", "суставы", "хрящи", "подвижность"],
        
        # Иммунитет и защита
        "иммунитет": ["защита", "здоровье", "immunopump", "protect", "протект"],
        "защита": ["иммунитет", "immunopump", "protect", "протект"],
        
        # Похудение и детокс
        "похудение": ["fire slim", "pro slim", "drainage", "detox", "жиросжигатель", "сжигание жира", "стройность", "снижение веса"],
        "детокс": ["detox", "очищение", "pure", "дренаж", "drainage"],
        "жир": ["fire slim", "pro slim", "жиросжигатель", "сжигание", "похудение"],
        "отеки": ["drainage", "дренаж", "дренирующий"],
        
        # Печень и ЖКТ
        "печень": ["lifresh", "livera", "очищение печени", "восстановление печени"],
        "жкт": ["metabiotic", "микрофлора", "пищеварение", "баланс"],
        "пищеварение": ["metabiotic", "микрофлора", "жкт", "баланс"],
        
        # Зрение
        "зрение": ["optics", "глаза", "острота зрения", "для зрения"],
        "глаза": ["optics", "зрение", "острота зрения"],
        
        # Витамины и минералы
        "железо": ["iron", "ирон", "хелат"],
        "омега": ["omega", "omega-3", "омега-3", "жирные кислоты"],
        "витамин д": ["vitamin d3", "д3", "витамин d", "кальций"],
        "кальций": ["vitamin d3", "mineral set", "минералы", "кости"],
        "минералы": ["mineral set", "минеральный комплекс", "микроэлементы"],
        
        # Кости и костная ткань (НЕ зубы!)
        "кости": ["костная ткань", "кальций", "витамин d3", "mineral set", "минеральный комплекс", "коллаген"],
        "костей": ["костная ткань", "кальций", "витамин d3", "mineral set", "минеральный комплекс", "коллаген"],
        "костная": ["кости", "кальций", "витамин d3", "mineral set"],
        
        # Коллаген и красота
        "коллаген": ["collagen", "hondroskin", "молодость", "суставы"],
        "молодость": ["коллаген", "collagen", "красота", "антивозрастной"],
        "красота": ["уход", "косметика"],
        
        # Косметика для лица (более точный поиск)
        "кожа лица": ["лицо", "face", "для лица", "косметика для лица"],
        "кожи лица": ["лицо", "face", "для лица", "косметика для лица"],
        "лицо": ["face", "для лица", "косметика для лица"],
        "маска": ["mask", "лицо"],
        "патчи": ["patches", "под глаза"],
        
        # Загар и защита от солнца
        "загар": ["tan water", "автозагар", "solar harmony", "солнцезащитный", "spf"],
        "от загара": ["solar harmony", "солнцезащитный", "spf", "защита от солнца"],
        "для загара": ["tan water", "автозагар"],
        "солнце": ["solar harmony", "солнцезащитный", "spf", "защита"],
        "spf": ["solar harmony", "солнцезащитный", "защита от солнца"],
        
        # Косметика для тела
        "крем": ["cream", "косметика", "уход"],
        "рук": ["hand", "для рук", "крем для рук", "hand cream"],
        "ног": ["foot", "для ног", "крем для ног", "foot cream"],
        "тело": ["body", "для тела", "крем для тела", "body cream", "скраб"],
        "косметика": ["уход", "крем", "маска", "тоник"],
        
        # Волосы
        "волосы": ["уход", "красота", "шампунь", "hair", "волос", "balance", "repair"],
        
        # Зубы
        "зубы": ["зубная паста", "keep smile", "полость рта", "отбеливание"],
        
        # Функциональное питание
        "протеин": ["protein", "белок", "bodybox", "спортивное питание"],
        "белок": ["protein", "протеин", "bodybox"],
        
        # Напитки
        "чай": ["tea", "фиточай", "pure", "breez", "happy", "stimul", "harmony", "livera"],
        "фиточай": ["pure", "breez", "happy", "stimul", "harmony", "livera", "чай"],
        
        # Дом и уборка
        "посуда": ["dish up", "для посуды", "средство для мытья"],
        "стирка": ["launder", "для стирки", "порошок", "soft"],
        "уборка": ["clean", "чистящее", "средство для уборки"],
    }
    
    # Добавляем синонимы к поиску
    expanded_words = query_words.copy()
    for word in query_words:
        for key, values in synonyms.items():
            if word in key or key in word:
                expanded_words.update(values)
    
    # Определяем исключающие термины (для мужских/женских продуктов)
    exclusions = []
    if any(word in query_lower for word in ["flame woman", "женский", "для нее"]):
        exclusions = ["flame man", "мужской фламе", "для него"]
    elif any(word in query_lower for word in ["flame man", "мужской", "для него", "мужская сила", "потенция"]):
        exclusions = ["flame woman", "женский фламе", "для нее"]
    
    # Для костей - исключаем зубные товары
    if any(word in query_lower for word in ["кост", "костей", "костная"]):
        exclusions.extend(["зубная щетка", "зубная паста", "для полости рта", "keep smile brush"])
    
    # Для кремов - различаем лицо/руки/ноги/тело
    if "для лица" in query_lower or "лицо" in query_lower:
        exclusions.extend(["для рук", "для ног", "для тела", "hand cream", "foot cream", "body cream"])
    elif "для рук" in query_lower:
        exclusions.extend(["для лица", "для ног", "для тела", "face", "foot cream", "body cream"])
    elif "для ног" in query_lower:
        exclusions.extend(["для лица", "для рук", "для тела", "face", "hand cream", "body cream"])
    
    results = []
    
    for product in catalog:
        score = 0
        name_lower = product.get("name", "").lower()
        tags_lower = ' '.join(product.get("tags", [])).lower()
        category = product.get("category", "")
        combined = f"{name_lower} {tags_lower}"
        
        # Проверка на исключающие термины
        if exclusions:
            # Если найден исключающий термин - сильно понижаем приоритет
            if any(excl.lower() in combined for excl in exclusions):
                score -= 10
        
        # Специальный бонус для категории при запросе про лицо
        if any(word in query_lower for word in ["лиц", "face"]):
            if category == "Косметика для лица":
                score += 15  # Очень высокий приоритет для точной категории
            elif category not in ["Косметика для лица"]:
                # Если запрашивают "для лица" но товар не из этой категории - сильно понижаем
                score -= 10
        
        # Специальный бонус для FLEX при запросе о суставах
        if any(word in query_lower for word in ["сустав", "связк", "хрящ"]):
            if "flex" in name_lower or "флекс" in name_lower:
                score += 10  # Высокий приоритет для FLEX
        
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
        
        # Search in name (with boosted priority for exact/partial matches)
        name_lower = product.get("name", "").lower()
        if query_lower in name_lower:
            score += 10  # Очень высокий приоритет для прямого совпадения в названии
        elif any(word in name_lower for word in expanded_words if len(word) > 3):
            # Только длинные слова (>3 букв) для избежания ложных совпадений
            score += 5
        
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
    
    # Фильтруем результаты: если есть высокоскоринговые товары (>10),
    # то убираем низкоскоринговые (<5) чтобы избежать нерелевантных результатов
    if results and results[0]["score"] > 10:
        # Есть явно релевантные товары - отсекаем слабые
        results = [r for r in results if r["score"] >= 5]
    
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

