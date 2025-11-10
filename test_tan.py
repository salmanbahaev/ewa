"""Test script for tan/sun protection search"""
import sys
sys.path.insert(0, '.')

from ai.product_search import search_products

queries = [
    "от загара",
    "для загара",
    "солнцезащитный крем"
]

for query in queries:
    print(f"\n{'='*80}")
    print(f"Поиск: '{query}'")
    print('='*80)
    
    products = search_products(query, max_results=5)
    
    print(f"Найдено: {len(products)} товаров\n")
    
    for idx, product in enumerate(products, 1):
        name = product.get('name', '')
        category = product.get('category', '')
        tags = product.get('tags', [])
        
        print(f"{idx}. {name}")
        print(f"   Категория: {category}")
        if tags:
            print(f"   Теги: {tags[0]}")

