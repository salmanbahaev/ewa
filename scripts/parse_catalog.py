"""
Парсер каталога товаров EWA Product с официального API
Получает полный актуальный каталог товаров с сайта
"""

import requests
import json
import re
from pathlib import Path
from typing import List, Dict, Any


API_URL = "https://ewaproduct.com/api/products/list?country_id=1"
OUTPUT_FILE = Path(__file__).parent.parent / "data" / "mainCatalog.json"


def clean_html(text: str) -> str:
    """Удаляет HTML-теги из текста"""
    if not text:
        return ""
    # Убираем HTML-теги
    text = re.sub(r'<[^>]+>', '', text)
    # Убираем лишние пробелы и переносы
    text = re.sub(r'\s+', ' ', text)
    # Убираем спецсимволы
    text = text.replace('\u003c', '<').replace('\u003e', '>')
    return text.strip()


def extract_price_rub(prices: List[Dict]) -> int:
    """Извлекает цену в рублях из массива цен"""
    for price_info in prices:
        if price_info.get("iso_code") == "643":  # Россия
            return price_info.get("price", 0) // 100  # Цена приходит в копейках
    return 0


def extract_tags(product: Dict) -> List[str]:
    """Извлекает теги из различных полей продукта"""
    tags = []
    
    # Теги из поля tags
    if product.get("tags"):
        for tag in product["tags"]:
            tag_clean = clean_html(tag).lower()
            if tag_clean:
                tags.append(tag_clean)
    
    # Теги из keywords
    if product.get("keywords"):
        keywords = product["keywords"].split(",")
        for kw in keywords:
            kw_clean = kw.strip().lower()
            if kw_clean and kw_clean not in tags:
                tags.append(kw_clean)
    
    # Категории как теги
    if product.get("categories"):
        for cat in product["categories"]:
            cat_clean = cat.strip().lower()
            if cat_clean and cat_clean not in tags:
                tags.append(cat_clean)
    
    return tags


def transform_product(product: Dict, index: int) -> Dict[str, Any]:
    """Преобразует продукт из API в наш формат"""
    
    # Основная информация
    product_id = f"P{str(product.get('id', index)).zfill(3)}"
    name = product.get("name", "Без названия")
    
    # Категория
    main_category = product.get("main_category", "")
    categories = product.get("categories", [])
    category = main_category if main_category else (categories[0] if categories else "Прочее")
    
    # Цена (из массива prices для России)
    item = product.get("single_item", {}).get("item", {})
    prices = item.get("prices", [])
    price_rub = extract_price_rub(prices)
    
    # Количество/объем
    packaging = product.get("attributes", {}).get("packaging", "")
    quantity_volume = packaging if packaging else None
    
    # Описание (из long_description или subtitle)
    long_desc = clean_html(product.get("long_description", ""))
    subtitle = product.get("attributes", {}).get("subtitle", "")
    description = long_desc if long_desc else subtitle
    
    # Теги
    tags = extract_tags(product)
    
    # URL товара на сайте
    slug = product.get("slug", "")
    product_url = f"https://ewaproduct.com/ru/product/{slug}" if slug else None
    
    # Картинка товара (первая из массива)
    images = item.get("images", [])
    image_url = images[0].get("src") if images else None
    
    return {
        "id": product_id,
        "api_id": product.get("id"),
        "name": name,
        "category": category,
        "subcategory": None,
        "price_rub": price_rub,
        "quantity_volume": quantity_volume,
        "description": description,
        "tags": tags,
        "slug": slug,
        "article": item.get("article", ""),
        "url": product_url,
        "image": image_url
    }


def fetch_catalog() -> List[Dict[str, Any]]:
    """Получает каталог товаров из API"""
    print(f"📡 Запрашиваю каталог товаров из {API_URL}...")
    
    try:
        response = requests.get(API_URL, timeout=30)
        response.raise_for_status()
        
        products_raw = response.json()
        print(f"✅ Получено {len(products_raw)} товаров")
        
        # Фильтруем только видимые товары
        products_raw = [p for p in products_raw if p.get("visible", True)]
        print(f"📦 Видимых товаров: {len(products_raw)}")
        
        # Трансформируем в наш формат
        products = []
        for idx, product_raw in enumerate(products_raw, start=1):
            try:
                product = transform_product(product_raw, idx)
                products.append(product)
            except Exception as e:
                print(f"⚠️  Ошибка обработки товара {product_raw.get('name', 'Unknown')}: {e}")
                continue
        
        print(f"✅ Успешно обработано {len(products)} товаров")
        return products
        
    except requests.RequestException as e:
        print(f"❌ Ошибка при запросе к API: {e}")
        return []
    except json.JSONDecodeError as e:
        print(f"❌ Ошибка парсинга JSON: {e}")
        return []


def save_catalog(products: List[Dict[str, Any]]) -> None:
    """Сохраняет каталог в JSON файл"""
    print(f"\n💾 Сохраняю каталог в {OUTPUT_FILE}...")
    
    try:
        # Создаем директорию если не существует
        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
        
        # Сохраняем с красивым форматированием
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(products, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Каталог сохранен: {len(products)} товаров")
        print(f"📄 Файл: {OUTPUT_FILE}")
        
        # Статистика по категориям
        categories = {}
        for product in products:
            cat = product["category"]
            categories[cat] = categories.get(cat, 0) + 1
        
        print("\n📊 Статистика по категориям:")
        for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            print(f"   • {cat}: {count} товаров")
        
    except Exception as e:
        print(f"❌ Ошибка сохранения файла: {e}")


def main():
    """Основная функция"""
    print("=" * 60)
    print("🛒 Парсер каталога EWA Product")
    print("=" * 60)
    
    # Получаем каталог
    products = fetch_catalog()
    
    if not products:
        print("\n❌ Не удалось получить товары. Проверьте подключение к интернету.")
        return
    
    # Сохраняем
    save_catalog(products)
    
    print("\n" + "=" * 60)
    print("✅ Парсинг завершен успешно!")
    print("=" * 60)


if __name__ == "__main__":
    main()

