from typing import Dict, Any, Optional, List
from browser_engine import BrowserEngine
from memory import Memory
from extractor import DataExtractor
import json
import re


class MarketRadarAgent:
    def __init__(self, browser_engine: BrowserEngine, memory: Memory, global_goal: str):
        self.browser = browser_engine
        self.memory = memory
        self.global_goal = global_goal
        self.extractor = DataExtractor(browser_engine)
        self.iteration_count = 0
        self.max_iterations = 50
        self.goal_achieved = False
    
    def analyze_goal(self) -> Dict[str, Any]:
        goal_lower = self.global_goal.lower()
        
        analysis = {
            "type": "unknown",
            "keywords": [],
            "target_data": [],
            "search_query": ""
        }
        
        if "preço" in goal_lower or "price" in goal_lower:
            analysis["type"] = "price_research"
            analysis["target_data"].append("prices")
        
        if "média" in goal_lower or "average" in goal_lower:
            analysis["type"] = "average_calculation"
        
        product_match = re.search(r'(?:preço|price|de|of)\s+([^em|in|no|na]+?)(?:\s+(?:em|in|no|na|brasil|brazil))', goal_lower)
        if product_match:
            product = product_match.group(1).strip()
            analysis["keywords"].append(product)
            analysis["search_query"] = f"{product} preço brasil"
        
        location_match = re.search(r'(?:em|in|no|na)\s+([^?]+)', goal_lower)
        if location_match:
            location = location_match.group(1).strip()
            analysis["keywords"].append(location)
            if not analysis["search_query"]:
                analysis["search_query"] = f"{self.global_goal}"
        
        if not analysis["search_query"]:
            analysis["search_query"] = self.global_goal
        
        return analysis
    
    def find_search_input(self, page_state: Dict[str, Any]) -> Optional[str]:
        elements = page_state.get("interactive_elements", [])
        
        for element in elements:
            if element.get("tag") == "input":
                element_id = element.get("id", "")
                if element_id and ("search" in element_id.lower() or "q" == element_id.lower()):
                    return f"#{element_id}"
        
        for element in elements:
            if element.get("tag") == "input":
                element_id = element.get("id", "")
                if element_id:
                    return f"#{element_id}"
        
        return "input[type='text']"
    
    def find_search_button(self, page_state: Dict[str, Any]) -> Optional[str]:
        elements = page_state.get("interactive_elements", [])
        
        for element in elements:
            text = element.get("text", "").lower()
            if "buscar" in text or "pesquisar" in text or "search" in text or "pesquisa" in text:
                element_id = element.get("id", "")
                if element_id:
                    return f"#{element_id}"
        
        for element in elements:
            if element.get("tag") == "button":
                element_id = element.get("id", "")
                if element_id:
                    return f"#{element_id}"
        
        return "button[type='submit'], input[type='submit']"
    
    def should_extract_data(self, page_state: Dict[str, Any]) -> bool:
        visible_text = page_state.get("visible_text", "").lower()
        
        price_indicators = ["r$", "preço", "price", "valor", "custo"]
        product_indicators = ["produto", "product", "item", "marca"]
        
        has_prices = any(indicator in visible_text for indicator in price_indicators)
        has_products = any(indicator in visible_text for indicator in product_indicators)
        
        return has_prices and has_products
    
    def decide_action(self, page_state: Dict[str, Any]) -> Dict[str, Any]:
        self.iteration_count += 1
        
        if self.iteration_count >= self.max_iterations:
            return {
                "thought_process": "Maximum iterations reached. Finishing mission.",
                "reasoning": "Preventing infinite loops.",
                "action": {"name": "finish", "params": {"summary": self.memory.get_summary()}},
                "is_goal_achieved": False
            }
        
        current_url = page_state.get("url", "")
        
        if self.memory.is_loop_detected(current_url):
            return {
                "thought_process": f"Loop detected on {current_url}. Changing strategy.",
                "reasoning": "Visited this URL 3+ times. Need to try different approach.",
                "action": {"name": "goto", "params": {"url": "https://www.google.com"}},
                "is_goal_achieved": False
            }
        
        goal_analysis = self.analyze_goal()
        visible_text = page_state.get("visible_text", "").lower()
        elements = page_state.get("interactive_elements", [])
        
        if self.should_extract_data(page_state) and not self.goal_achieved:
            prices = self.extractor.extract_prices()
            if prices:
                extracted = self.extractor.extract_structured_data(["prices", "product_names", "url", "title"])
                self.memory.add_extracted_data(extracted)
                
                if goal_analysis["type"] == "average_calculation" and len(prices) >= 3:
                    avg_price = sum(p["value"] for p in prices) / len(prices)
                    self.memory.add_extracted_data({"average_price": avg_price, "currency": "BRL"})
                    self.goal_achieved = True
                    return {
                        "thought_process": f"Extracted {len(prices)} prices. Average calculated.",
                        "reasoning": "Sufficient data gathered to calculate average.",
                        "action": {"name": "finish", "params": {"summary": self.memory.get_summary()}},
                        "is_goal_achieved": True
                    }
        
        if "google" in current_url.lower() or current_url == "" or "google.com" in current_url:
            search_input = self.find_search_input(page_state)
            if search_input:
                return {
                    "thought_process": "On Google homepage. Preparing to search for the product.",
                    "reasoning": f"Found search input. Will type search query and press Enter: {goal_analysis['search_query']}",
                    "action": {
                        "name": "type",
                        "params": {
                            "selector": search_input,
                            "text": goal_analysis["search_query"],
                            "press_enter": True
                        }
                    },
                    "is_goal_achieved": False
                }
        
        if any("search" in el.get("id", "").lower() or "q" == el.get("id", "").lower() for el in elements):
            search_input = self.find_search_input(page_state)
            
            if search_input:
                return {
                    "thought_process": "Found search input on page. Will enter search query and submit.",
                    "reasoning": f"Search input available. Typing and submitting: {goal_analysis['search_query']}",
                    "action": {
                        "name": "type",
                        "params": {
                            "selector": search_input,
                            "text": goal_analysis["search_query"],
                            "press_enter": True
                        }
                    },
                    "is_goal_achieved": False
                }
        
        if any("buscar" in el.get("text", "").lower() or "search" in el.get("text", "").lower() for el in elements):
            search_button = self.find_search_button(page_state)
            if search_button:
                return {
                    "thought_process": "Found search button. Will click to execute search.",
                    "reasoning": f"Clicking search button to execute query.",
                    "action": {
                        "name": "click",
                        "params": {
                            "selector": search_button
                        }
                    },
                    "is_goal_achieved": False
                }
        
        if any(keyword in visible_text for keyword in goal_analysis["keywords"]):
            if self.should_extract_data(page_state):
                return {
                    "thought_process": "Relevant content found. Extracting data before continuing.",
                    "reasoning": "Page contains product and price information. Extracting data.",
                    "action": {
                        "name": "extract",
                        "params": {
                            "data_points": ["prices", "product_names", "url", "title"]
                        }
                    },
                    "is_goal_achieved": False
                }
            else:
                return {
                    "thought_process": "Relevant content found but no clear data structure. Scrolling to find more content.",
                    "reasoning": "Need to scroll to trigger lazy loading or find product listings.",
                    "action": {
                        "name": "scroll",
                        "params": {
                            "direction": "down"
                        }
                    },
                    "is_goal_achieved": False
                }
        
        if len(elements) > 0:
            first_link = None
            for element in elements:
                if element.get("tag") == "a" and element.get("text", ""):
                    text = element.get("text", "").lower()
                    if any(keyword in text for keyword in goal_analysis["keywords"]):
                        element_id = element.get("id", "")
                        if element_id:
                            first_link = f"#{element_id}"
                            break
            
            if first_link:
                return {
                    "thought_process": f"Found relevant link matching keywords. Clicking to navigate.",
                    "reasoning": f"Link contains relevant keywords: {goal_analysis['keywords']}",
                    "action": {
                        "name": "click",
                        "params": {
                            "selector": first_link
                        }
                    },
                    "is_goal_achieved": False
                }
        
        return {
            "thought_process": "No clear action found. Scrolling to reveal more content.",
            "reasoning": "Scrolling down to trigger lazy loading or reveal hidden elements.",
            "action": {
                "name": "scroll",
                "params": {
                    "direction": "down"
                }
            },
            "is_goal_achieved": False
        }
    
    def execute_action(self, action_command: Dict[str, Any]) -> Dict[str, Any]:
        action_name = action_command["action"]["name"]
        params = action_command["action"]["params"]
        
        result = {"success": False, "error": "Unknown action"}
        
        if action_name == "goto":
            result = self.browser.goto(params["url"])
            self.memory.add_action("goto", params, params["url"], str(result))
        
        elif action_name == "click":
            result = self.browser.click(params["selector"])
            self.memory.add_action("click", params, self.browser.current_url, str(result))
        
        elif action_name == "type":
            press_enter = params.get("press_enter", False)
            result = self.browser.type(params["selector"], params["text"], press_enter=press_enter)
            self.memory.add_action("type", params, self.browser.current_url, str(result))
        
        elif action_name == "scroll":
            result = self.browser.scroll(params["direction"])
            self.memory.add_action("scroll", params, self.browser.current_url, str(result))
        
        elif action_name == "wait":
            result = self.browser.wait(params["seconds"])
            self.memory.add_action("wait", params, self.browser.current_url, str(result))
        
        elif action_name == "extract":
            extracted = self.extractor.extract_structured_data(params["data_points"])
            self.memory.add_extracted_data(extracted)
            result = {"success": True, "data": extracted}
            self.memory.add_action("extract", params, self.browser.current_url, str(result))
        
        elif action_name == "finish":
            result = {"success": True, "summary": params.get("summary", "")}
            self.goal_achieved = action_command.get("is_goal_achieved", False)
        
        return result
    
    def step(self) -> str:
        page_state = self.browser.get_page_state()
        action_command = self.decide_action(page_state)
        result = self.execute_action(action_command)
        
        response = {
            "thought_process": action_command["thought_process"],
            "reasoning": action_command["reasoning"],
            "action": action_command["action"],
            "is_goal_achieved": action_command["is_goal_achieved"],
            "result": result
        }
        
        return json.dumps(response, indent=2, ensure_ascii=False)
