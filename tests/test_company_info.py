"""Tests for company info retrieval"""
import pytest
from ai.product_search import get_company_info


def test_get_company_info():
    """Test getting company information"""
    info = get_company_info("company")
    
    assert "company" in info
    assert info["company"]["company"]["name"] == "EWA PRODUCT"
    assert info["company"]["company"]["foundation"] == "2022"


def test_get_business_info():
    """Test getting business information"""
    info = get_company_info("business")
    
    assert "business" in info
    assert "business_overview" in info["business"]


def test_get_events_info():
    """Test getting events information"""
    info = get_company_info("events")
    
    assert "events" in info
    assert "events" in info["events"]
    assert isinstance(info["events"]["events"], list)


def test_get_geography_all():
    """Test getting all geography info"""
    info = get_company_info("geography")
    
    assert "geography" in info
    assert isinstance(info["geography"], list)
    assert len(info["geography"]) > 0


def test_get_geography_by_city():
    """Test filtering geography by city"""
    info = get_company_info("geography", city="Москва")
    
    assert "geography" in info
    # Should find Moscow office
    moscow_offices = [loc for loc in info["geography"] if "Москва" in loc["city"]]
    assert len(moscow_offices) > 0


def test_get_all_info():
    """Test getting all company info at once"""
    info = get_company_info("all")
    
    assert "company" in info
    assert "business" in info
    assert "events" in info
    assert "geography" in info


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

