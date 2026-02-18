"""Unit tests for DataExtractor."""
import pytest
from unittest.mock import Mock, patch
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from infrastructure.extractor import DataExtractor


class TestDataExtractor:
    """Test suite for DataExtractor."""
    
    @pytest.fixture
    def extractor(self, mock_browser_engine):
        """Create DataExtractor with mocked browser."""
        return DataExtractor(mock_browser_engine)
    
    def test_extract_prices_brl(self, extractor, mock_browser_engine):
        """Test extracting BRL prices."""
        mock_browser_engine.get_page_state.return_value = {
            "visible_text": "R$ 50,00 R$ 100.50 R$ 75,99",
            "url": "https://example.com",
            "title": "Test"
        }
        
        prices = extractor.extract_prices("BRL")
        
        assert len(prices) == 3
        assert prices[0]["value"] == 50.0
        assert prices[0]["currency"] == "BRL"
        assert prices[1]["value"] == 100.5
    
    def test_extract_prices_usd(self, extractor, mock_browser_engine):
        """Test extracting USD prices."""
        mock_browser_engine.get_page_state.return_value = {
            "visible_text": "$ 25.99 $ 50.00",
            "url": "https://example.com",
            "title": "Test"
        }
        
        prices = extractor.extract_prices("USD")
        
        assert len(prices) == 2
        assert prices[0]["currency"] == "USD"
    
    def test_extract_product_names(self, extractor, mock_browser_engine):
        """Test extracting product names."""
        mock_browser_engine.get_page_state.return_value = {
            "visible_text": "Creatine 300g Whey Protein 1kg",
            "interactive_elements": [
                {"id": "product-1", "tag": "div", "text": "Creatine Monohydrate 300g"},
                {"id": "product-2", "tag": "div", "text": "Whey Protein 1kg"}
            ],
            "url": "https://example.com",
            "title": "Test"
        }
        
        products = extractor.extract_product_names()
        
        assert len(products) > 0
        assert any("creatine" in p.lower() for p in products)
    
    def test_extract_structured_data(self, extractor, mock_browser_engine):
        """Test extracting structured data."""
        mock_browser_engine.get_page_state.return_value = {
            "visible_text": "R$ 50,00 Product Name",
            "interactive_elements": [],
            "url": "https://example.com",
            "title": "Test Page"
        }
        
        data = extractor.extract_structured_data(["prices", "url", "title"])
        
        assert "prices" in data
        assert "url" in data
        assert "title" in data
        assert data["url"] == "https://example.com"
        assert data["title"] == "Test Page"
    
    def test_extract_description(self, extractor, mock_browser_engine):
        """Test extracting description."""
        long_text = "This is a long description " * 10
        mock_browser_engine.get_page_state.return_value = {
            "visible_text": long_text,
            "url": "https://example.com",
            "title": "Test"
        }
        
        description = extractor.extract_description(mock_browser_engine.get_page_state())
        
        assert len(description) > 0
        assert len(description) <= 300
    
    def test_extract_specifications(self, extractor, mock_browser_engine):
        """Test extracting specifications."""
        mock_browser_engine.get_page_state.return_value = {
            "visible_text": "Weight: 300g\nBrand: Test Brand\nPrice: R$ 50,00",
            "url": "https://example.com",
            "title": "Test"
        }
        
        specs = extractor.extract_specifications(mock_browser_engine.get_page_state())
        
        assert isinstance(specs, dict)
        assert len(specs) > 0
