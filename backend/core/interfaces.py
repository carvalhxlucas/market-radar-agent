"""Interfaces (Protocols) for dependency injection."""
from typing import Protocol, Dict, Any, List, Optional
from core.domain.models import ExtractedData, ActionHistory


class IBrowserEngine(Protocol):
    """Interface for browser engine."""
    
    def start(self) -> None:
        """Start the browser."""
        ...
    
    def stop(self) -> None:
        """Stop the browser."""
        ...
    
    def goto(self, url: str) -> Dict[str, Any]:
        """Navigate to URL."""
        ...
    
    def click(self, selector: str) -> Dict[str, Any]:
        """Click on element."""
        ...
    
    def type(self, selector: str, text: str, press_enter: bool = False) -> Dict[str, Any]:
        """Type text into element."""
        ...
    
    def scroll(self, direction: str) -> Dict[str, Any]:
        """Scroll page."""
        ...
    
    def wait(self, seconds: float) -> Dict[str, Any]:
        """Wait for specified time."""
        ...
    
    def get_page_state(self) -> Dict[str, Any]:
        """Get current page state."""
        ...


class IMemory(Protocol):
    """Interface for memory storage."""
    
    def add_action(self, action: str, params: Dict[str, Any], url: str, result: str = "") -> None:
        """Add action to history."""
        ...
    
    def is_loop_detected(self, url: str) -> bool:
        """Check if loop is detected."""
        ...
    
    def get_recent_actions(self, count: int = 10) -> List[ActionHistory]:
        """Get recent actions."""
        ...
    
    def add_extracted_data(self, data: Dict[str, Any]) -> None:
        """Add extracted data."""
        ...
    
    def get_extracted_data(self) -> List[ExtractedData]:
        """Get all extracted data."""
        ...
    
    def get_summary(self) -> str:
        """Get mission summary."""
        ...


class IDataExtractor(Protocol):
    """Interface for data extraction."""
    
    def extract_prices(self, currency: str = "BRL") -> List[Dict[str, Any]]:
        """Extract prices from page."""
        ...
    
    def extract_product_names(self) -> List[str]:
        """Extract product names from page."""
        ...
    
    def extract_structured_data(self, data_points: List[str]) -> Dict[str, Any]:
        """Extract structured data from page."""
        ...
