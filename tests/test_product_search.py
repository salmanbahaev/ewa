"""Tests for product search functionality"""
import pytest
from ai.product_search import search_products


def test_search_products_by_tags():
    """Test searching products by tags"""
    # Search for brain/memory products
    results = search_products("мозг память", max_results=5)
    
    assert len(results) > 0, "Should find products related to brain/memory"
    
    # Check that BRAINSTORM is in results
    product_names = [p["name"] for p in results]
    assert any("BRAINSTORM" in name for name in product_names), "BRAINSTORM should be found"


def test_search_products_by_category():
    """Test searching products by category"""
    # Search for biohacking category
    results = search_products("биохакинг", max_results=10)
    
    assert len(results) > 0, "Should find biohacking products"
    
    # Check that results have correct category
    for product in results[:3]:  # Check first 3
        assert product["category"] == "БИОХАКИНГ", f"Product {product['name']} should be in БИОХАКИНГ category"


def test_search_products_no_results():
    """Test search with query that has no results"""
    results = search_products("абсолютно несуществующий продукт xyz123", max_results=5)
    
    assert len(results) == 0, "Should return empty list for non-existent products"


def test_search_products_vitamin_c():
    """Test searching for vitamin C products"""
    results = search_products("витамин С иммунитет", max_results=5)
    
    assert len(results) > 0, "Should find vitamin C related products"


def test_search_products_sleep():
    """Test searching for sleep-related products"""
    results = search_products("сон успокоение", max_results=5)
    
    # May or may not find products, just test that it doesn't crash
    assert isinstance(results, list), "Should return a list"


def test_search_products_max_results():
    """Test that max_results parameter works"""
    results = search_products("здоровье", max_results=3)
    
    assert len(results) <= 3, "Should return at most 3 results"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

