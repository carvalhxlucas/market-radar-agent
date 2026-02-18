"""Unit tests for BrowserEngine."""
import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from infrastructure.browser_engine import BrowserEngine


class TestBrowserEngine:
    """Test suite for BrowserEngine."""
    
    @pytest.fixture
    def browser_engine(self):
        """Create BrowserEngine instance."""
        return BrowserEngine(headless=True)
    
    @patch('infrastructure.browser_engine.sync_playwright')
    def test_start(self, mock_playwright, browser_engine):
        """Test starting the browser."""
        mock_playwright_instance = MagicMock()
        mock_browser = MagicMock()
        mock_context = MagicMock()
        mock_page = MagicMock()
        
        mock_playwright.return_value.start.return_value = mock_playwright_instance
        mock_playwright_instance.chromium.launch.return_value = mock_browser
        mock_browser.new_context.return_value = mock_context
        mock_context.new_page.return_value = mock_page
        
        browser_engine.start()
        
        assert browser_engine.browser is not None
        assert browser_engine.context is not None
        assert browser_engine.page is not None
    
    def test_stop(self, browser_engine):
        """Test stopping the browser."""
        # Mock browser components
        browser_engine.page = Mock()
        browser_engine.context = Mock()
        browser_engine.browser = Mock()
        browser_engine.playwright = Mock()
        
        browser_engine.stop()
        
        browser_engine.page.close.assert_called_once()
        browser_engine.context.close.assert_called_once()
        browser_engine.browser.close.assert_called_once()
        browser_engine.playwright.stop.assert_called_once()
    
    def test_goto_success(self, browser_engine):
        """Test successful navigation."""
        browser_engine.page = Mock()
        browser_engine.page.goto = Mock()
        browser_engine.page.url = "https://example.com"
        
        result = browser_engine.goto("https://example.com")
        
        assert result["success"] is True
        assert result["url"] == "https://example.com"
        browser_engine.page.goto.assert_called_once()
    
    def test_goto_failure(self, browser_engine):
        """Test navigation failure."""
        browser_engine.page = Mock()
        browser_engine.page.goto = Mock(side_effect=Exception("Connection error"))
        
        result = browser_engine.goto("https://example.com")
        
        assert result["success"] is False
        assert "error" in result
    
    def test_click_success(self, browser_engine):
        """Test successful click."""
        browser_engine.page = Mock()
        mock_element = Mock()
        browser_engine.page.query_selector = Mock(return_value=mock_element)
        browser_engine.page.url = "https://example.com"
        
        result = browser_engine.click("#button")
        
        assert result["success"] is True
        mock_element.scroll_into_view_if_needed.assert_called_once()
        mock_element.click.assert_called_once()
    
    def test_click_element_not_found(self, browser_engine):
        """Test click when element not found."""
        browser_engine.page = Mock()
        browser_engine.page.query_selector = Mock(return_value=None)
        
        result = browser_engine.click("#button")
        
        assert result["success"] is False
        assert "not found" in result["error"].lower()
    
    def test_type_success(self, browser_engine):
        """Test successful typing."""
        browser_engine.page = Mock()
        mock_element = Mock()
        browser_engine.page.query_selector = Mock(return_value=mock_element)
        
        result = browser_engine.type("#input", "test text", press_enter=False)
        
        assert result["success"] is True
        mock_element.fill.assert_called_once()
        mock_element.type.assert_called_once()
    
    def test_type_with_enter(self, browser_engine):
        """Test typing with Enter press."""
        browser_engine.page = Mock()
        mock_element = Mock()
        browser_engine.page.query_selector = Mock(return_value=mock_element)
        browser_engine.page.url = "https://example.com"
        
        result = browser_engine.type("#input", "test text", press_enter=True)
        
        assert result["success"] is True
        mock_element.press.assert_called_once_with("Enter")
    
    def test_scroll_down(self, browser_engine):
        """Test scrolling down."""
        browser_engine.page = Mock()
        browser_engine.page.evaluate = Mock()
        
        result = browser_engine.scroll("down")
        
        assert result["success"] is True
        browser_engine.page.evaluate.assert_called_once()
    
    def test_scroll_up(self, browser_engine):
        """Test scrolling up."""
        browser_engine.page = Mock()
        browser_engine.page.evaluate = Mock()
        
        result = browser_engine.scroll("up")
        
        assert result["success"] is True
        browser_engine.page.evaluate.assert_called_once()
    
    def test_scroll_invalid_direction(self, browser_engine):
        """Test scrolling with invalid direction."""
        result = browser_engine.scroll("invalid")
        
        assert result["success"] is False
        assert "direction" in result["error"].lower()
    
    def test_wait(self, browser_engine):
        """Test wait functionality."""
        result = browser_engine.wait(1.0)
        
        assert result["success"] is True
    
    def test_get_page_state(self, browser_engine):
        """Test getting page state."""
        browser_engine.page = Mock()
        browser_engine.current_url = "https://example.com"
        browser_engine.page.evaluate = Mock(side_effect=[
            [],  # interactive_elements
            "Page content"  # visible_text
        ])
        browser_engine.page.title = Mock(return_value="Test Page")
        
        state = browser_engine.get_page_state()
        
        assert state["url"] == "https://example.com"
        assert state["title"] == "Test Page"
        assert "interactive_elements" in state
        assert "visible_text" in state
