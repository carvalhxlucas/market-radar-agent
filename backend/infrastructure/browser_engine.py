"""Browser engine implementation using Playwright."""
from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext
from typing import Dict, Any, Optional
import time
from config.settings import Settings


class BrowserEngine:
    """Browser engine for web automation using Playwright."""
    
    def __init__(self, headless: bool = None):
        """
        Initialize browser engine.
        
        Args:
            headless: Whether to run in headless mode (defaults to settings)
        """
        self.settings = Settings()
        self.headless = headless if headless is not None else self.settings.browser_headless
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.current_url = ""
    
    def start(self) -> None:
        """Start the browser and create context."""
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=self.headless)
        self.context = self.browser.new_context(
            viewport={
                "width": self.settings.browser_viewport_width,
                "height": self.settings.browser_viewport_height
            },
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        self.page = self.context.new_page()
    
    def stop(self) -> None:
        """Stop the browser and cleanup resources."""
        if self.page:
            self.page.close()
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
    
    def goto(self, url: str) -> Dict[str, Any]:
        """
        Navigate to URL.
        
        Args:
            url: URL to navigate to
            
        Returns:
            Dictionary with success status and URL
        """
        try:
            self.page.goto(
                url,
                wait_until="networkidle",
                timeout=self.settings.browser_timeout
            )
            self.current_url = self.page.url
            return {"success": True, "url": self.current_url}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def click(self, selector: str) -> Dict[str, Any]:
        """
        Click on element.
        
        Args:
            selector: CSS selector for element
            
        Returns:
            Dictionary with success status
        """
        try:
            element = self.page.query_selector(selector)
            if not element:
                return {"success": False, "error": f"Element not found: {selector}"}
            
            element.scroll_into_view_if_needed()
            element.click(timeout=5000)
            time.sleep(1)
            self.current_url = self.page.url
            return {"success": True, "url": self.current_url}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def type(self, selector: str, text: str, press_enter: bool = False) -> Dict[str, Any]:
        """
        Type text into element.
        
        Args:
            selector: CSS selector for element
            text: Text to type
            press_enter: Whether to press Enter after typing
            
        Returns:
            Dictionary with success status
        """
        try:
            element = self.page.query_selector(selector)
            if not element:
                return {"success": False, "error": f"Element not found: {selector}"}
            
            element.scroll_into_view_if_needed()
            element.fill("")
            element.type(text, delay=50)
            if press_enter:
                element.press("Enter")
                time.sleep(2)
                self.current_url = self.page.url
            else:
                time.sleep(0.5)
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def scroll(self, direction: str) -> Dict[str, Any]:
        """
        Scroll page.
        
        Args:
            direction: Scroll direction ('down' or 'up')
            
        Returns:
            Dictionary with success status
        """
        try:
            if direction == "down":
                self.page.evaluate("window.scrollBy(0, window.innerHeight)")
            elif direction == "up":
                self.page.evaluate("window.scrollBy(0, -window.innerHeight)")
            else:
                return {"success": False, "error": "Direction must be 'down' or 'up'"}
            
            time.sleep(1)
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def wait(self, seconds: float) -> Dict[str, Any]:
        """
        Wait for specified time.
        
        Args:
            seconds: Number of seconds to wait
            
        Returns:
            Dictionary with success status
        """
        time.sleep(seconds)
        return {"success": True}
    
    def get_page_state(self) -> Dict[str, Any]:
        """
        Get current page state.
        
        Returns:
            Dictionary with page state information
        """
        try:
            interactive_elements = self.page.evaluate("""
                () => {
                    const elements = [];
                    const selectors = ['input', 'button', 'a', '[onclick]', '[role="button"]', 'select', 'textarea'];
                    selectors.forEach(selector => {
                        document.querySelectorAll(selector).forEach((el, idx) => {
                            if (el.offsetParent !== null) {
                                const rect = el.getBoundingClientRect();
                                if (rect.width > 0 && rect.height > 0) {
                                    const href = el.href || el.getAttribute('href') || '';
                                    elements.push({
                                        id: el.id || `${selector}_${idx}`,
                                        tag: el.tagName.toLowerCase(),
                                        text: el.textContent?.trim().substring(0, 100) || '',
                                        href: href,
                                        selector: selector,
                                        visible: true
                                    });
                                }
                            }
                        });
                    });
                    return elements;
                }
            """)
            
            visible_text = self.page.evaluate("""
                () => {
                    return document.body.innerText.substring(0, 2000);
                }
            """)
            
            return {
                "url": self.current_url,
                "interactive_elements": interactive_elements,
                "visible_text": visible_text,
                "title": self.page.title()
            }
        except Exception as e:
            return {"error": str(e)}
    
    def extract_data(self, selectors: Dict[str, str]) -> Dict[str, Any]:
        """
        Extract data using CSS selectors.
        
        Args:
            selectors: Dictionary mapping keys to CSS selectors
            
        Returns:
            Dictionary with extracted data
        """
        extracted = {}
        for key, selector in selectors.items():
            try:
                elements = self.page.query_selector_all(selector)
                if elements:
                    values = [el.inner_text() for el in elements]
                    extracted[key] = values if len(values) > 1 else values[0] if values else None
                else:
                    extracted[key] = None
            except Exception as e:
                extracted[key] = f"Error: {str(e)}"
        
        return extracted
