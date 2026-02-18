"""Data extraction implementation."""
from typing import Dict, Any, List
from infrastructure.browser_engine import BrowserEngine
import re


class DataExtractor:
    def __init__(self, browser_engine: BrowserEngine):
        self.browser = browser_engine
    
    def extract_prices(self, currency: str = "BRL") -> List[Dict[str, Any]]:
        page_state = self.browser.get_page_state()
        visible_text = page_state.get("visible_text", "")
        
        price_patterns = {
            "BRL": r'R\$\s*([\d.,]+)',
            "USD": r'\$\s*([\d.,]+)',
            "EUR": r'€\s*([\d.,]+)'
        }
        
        pattern = price_patterns.get(currency, price_patterns["BRL"])
        prices = []
        
        matches = re.finditer(pattern, visible_text)
        for match in matches:
            price_str = match.group(1).replace(".", "").replace(",", ".")
            try:
                price_value = float(price_str)
                prices.append({
                    "value": price_value,
                    "currency": currency,
                    "raw": match.group(0)
                })
            except ValueError:
                continue
        
        return prices
    
    def extract_product_names(self) -> List[str]:
        page_state = self.browser.get_page_state()
        elements = page_state.get("interactive_elements", [])
        visible_text = page_state.get("visible_text", "")
        
        products = []
        
        for element in elements:
            text = element.get("text", "").strip()
            element_id = element.get("id", "").lower()
            
            if text and len(text) > 3 and len(text) < 200:
                if any(keyword in element_id for keyword in ["product", "item", "title", "name"]):
                    products.append(text)
                elif any(keyword in text.lower() for keyword in ["mg", "g", "kg", "ml", "l", "unidade", "un"]):
                    products.append(text)
        
        lines = visible_text.split("\n")
        for line in lines:
            line = line.strip()
            if len(line) > 5 and len(line) < 150:
                if any(keyword in line.lower() for keyword in ["creatina", "creatine", "whey", "proteína", "protein"]):
                    products.append(line)
        
        return list(set(products))[:20]
    
    def extract_structured_data(self, data_points: List[str]) -> Dict[str, Any]:
        extracted = {}
        page_state = self.browser.get_page_state()
        
        for point in data_points:
            if point == "prices":
                extracted["prices"] = self.extract_prices()
            elif point == "product_names":
                extracted["product_names"] = self.extract_product_names()
            elif point == "url":
                extracted["url"] = page_state.get("url", "")
            elif point == "title":
                extracted["title"] = page_state.get("title", "")
            elif point == "description":
                extracted["description"] = self.extract_description(page_state)
            elif point == "specifications":
                extracted["specifications"] = self.extract_specifications(page_state)
            else:
                extracted[point] = self._extract_custom_point(point, page_state)
        
        return extracted
    
    def extract_description(self, page_state: Dict[str, Any]) -> str:
        """Extract main description or summary from page"""
        visible_text = page_state.get("visible_text", "")
        
        # Try to find meta description or first substantial paragraph
        lines = visible_text.split("\n")
        for line in lines:
            line = line.strip()
            if len(line) > 50 and len(line) < 500:
                # Likely a description
                return line
        
        # Return first 300 characters as fallback
        return visible_text[:300] if visible_text else ""
    
    def extract_specifications(self, page_state: Dict[str, Any]) -> Dict[str, str]:
        """Extract specifications in key-value format"""
        visible_text = page_state.get("visible_text", "")
        specs = {}
        
        # Look for common specification patterns
        spec_patterns = [
            r'([^:]+):\s*([^\n]+)',
            r'([^=]+)=\s*([^\n]+)',
            r'([A-Z][^:]+):\s*([^\n]+)'
        ]
        
        for pattern in spec_patterns:
            matches = re.finditer(pattern, visible_text)
            for match in matches:
                key = match.group(1).strip()
                value = match.group(2).strip()
                if len(key) < 50 and len(value) < 200:
                    specs[key] = value
        
        return specs
    
    def _extract_custom_point(self, point: str, page_state: Dict[str, Any]) -> Any:
        visible_text = page_state.get("visible_text", "").lower()
        point_lower = point.lower()
        
        if point_lower in visible_text:
            idx = visible_text.find(point_lower)
            snippet = visible_text[max(0, idx-50):idx+100]
            return snippet.strip()
        
        return None
