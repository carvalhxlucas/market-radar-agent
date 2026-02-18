from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext
from typing import Dict, Any, Optional, List
import time
import json


class BrowserEngine:
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.current_url = ""
    
    def start(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=self.headless)
        self.context = self.browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        self.page = self.context.new_page()
    
    def stop(self):
        if self.page:
            self.page.close()
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
    
    def goto(self, url: str) -> Dict[str, Any]:
        try:
            self.page.goto(url, wait_until="networkidle", timeout=30000)
            self.current_url = self.page.url
            return {"success": True, "url": self.current_url}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def click(self, selector: str) -> Dict[str, Any]:
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
        time.sleep(seconds)
        return {"success": True}
    
    def get_page_state(self) -> Dict[str, Any]:
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
                                    elements.push({
                                        id: el.id || `${selector}_${idx}`,
                                        tag: el.tagName.toLowerCase(),
                                        text: el.textContent?.trim().substring(0, 100) || '',
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
