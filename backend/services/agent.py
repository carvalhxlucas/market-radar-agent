"""MarketRadar agent implementation."""
from typing import Dict, Any, Optional, List
from infrastructure.browser_engine import BrowserEngine
from infrastructure.memory import Memory
from infrastructure.extractor import DataExtractor
from config.settings import Settings
from core.domain.models import GoalAnalysis
import json
import re


class MarketRadarAgent:
    def __init__(self, browser_engine: BrowserEngine, memory: Memory, global_goal: str):
        """
        Initialize MarketRadar agent.
        
        Args:
            browser_engine: Browser engine instance
            memory: Memory instance for state management
            global_goal: Mission goal
        """
        self.settings = Settings()
        self.browser = browser_engine
        self.memory = memory
        self.global_goal = global_goal
        self.extractor = DataExtractor(browser_engine)
        self.iteration_count = 0
        self.max_iterations = self.settings.agent_max_iterations
        self.goal_achieved = False
        self.research_phase = "initial"  # initial, searching, collecting, consolidating
        self.sources_visited = []
        self.target_sources = []
        self.min_sources = self.settings.agent_min_sources
        self.data_collection_count = 0
    
    def analyze_goal(self) -> Dict[str, Any]:
        goal_lower = self.global_goal.lower()
        
        analysis = {
            "type": "general_research",
            "keywords": [],
            "target_data": ["prices", "product_names", "descriptions", "specifications", "reviews", "comparisons"],
            "search_queries": [],
            "topic": ""
        }
        
        # Extract main topic
        if "preço" in goal_lower or "price" in goal_lower:
            analysis["type"] = "price_research"
            analysis["target_data"].append("prices")
        
        if "média" in goal_lower or "average" in goal_lower:
            analysis["type"] = "average_calculation"
        
        # Extract product/topic name
        product_match = re.search(r'(?:preço|price|de|of|sobre|about)\s+([^em|in|no|na|?]+?)(?:\s+(?:em|in|no|na|brasil|brazil|?))', goal_lower)
        if product_match:
            product = product_match.group(1).strip()
            analysis["keywords"].append(product)
            analysis["topic"] = product
        
        location_match = re.search(r'(?:em|in|no|na)\s+([^?]+)', goal_lower)
        if location_match:
            location = location_match.group(1).strip()
            analysis["keywords"].append(location)
        
        # Generate multiple search queries for comprehensive research
        topic = analysis["topic"] or self.global_goal
        analysis["search_queries"] = [
            f"{topic}",
            f"{topic} preço brasil",
            f"{topic} mercado brasil",
            f"{topic} informações",
            f"{topic} dados"
        ]
        
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
        current_url = page_state.get("url", "").lower()
        
        # Skip search engines and social media
        if any(domain in current_url for domain in self.settings.skip_domains):
            return False
        
        # Indicators of valuable content
        content_indicators = [
            "r$", "preço", "price", "valor", "custo",
            "produto", "product", "item", "marca",
            "especificação", "specification", "característica",
            "informação", "information", "dados", "data",
            "análise", "analysis", "comparação", "comparison",
            "revisão", "review", "avaliação", "evaluation"
        ]
        
        has_content = any(indicator in visible_text for indicator in content_indicators)
        
        # Check if page has substantial content (not just navigation)
        word_count = len(visible_text.split())
        has_substantial_content = word_count > 100
        
        return has_content and has_substantial_content
    
    def is_trusted_source(self, url: str) -> bool:
        """
        Identify trusted sources for research.
        
        Args:
            url: URL to check
            
        Returns:
            True if URL is from a trusted domain
        """
        url_lower = url.lower()
        return any(domain in url_lower for domain in self.settings.trusted_domains)
    
    def should_visit_link(self, element: Dict[str, Any], goal_analysis: Dict[str, Any]) -> bool:
        """Determine if a link should be visited based on relevance"""
        text = element.get("text", "").lower()
        url = element.get("href", "").lower() if "href" in element else ""
        
        # Check if link text contains relevant keywords
        has_keywords = any(keyword in text for keyword in goal_analysis["keywords"])
        
        # Check if it's a trusted source
        is_trusted = self.is_trusted_source(url) if url else False
        
        # Check if it's not already visited
        is_new = url not in self.sources_visited if url else True
        
        return (has_keywords or is_trusted) and is_new and len(text) > 5
    
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
        
        # Extract data from current page if it's a valuable source
        if self.should_extract_data(page_state):
            if current_url not in self.sources_visited:
                self.sources_visited.append(current_url)
                self.data_collection_count += 1
                
                # Extract comprehensive structured data
                extracted = self.extractor.extract_structured_data(
                    goal_analysis["target_data"] + ["url", "title"]
                )
                self.memory.add_extracted_data(extracted)
                
                # Check if we have enough sources
                if len(self.sources_visited) >= self.min_sources and self.data_collection_count >= self.min_sources:
                    if goal_analysis["type"] == "average_calculation":
                        all_prices = []
                        for data in self.memory.get_extracted_data():
                            if "prices" in data:
                                prices = data["prices"]
                                if isinstance(prices, list):
                                    for p in prices:
                                        if isinstance(p, dict):
                                            all_prices.append(p["value"])
                                        else:
                                            all_prices.append(p)
                                else:
                                    all_prices.append(prices)
                        
                        if len(all_prices) >= 3:
                            avg_price = sum(all_prices) / len(all_prices)
                            self.memory.add_extracted_data({"average_price": avg_price, "currency": "BRL"})
                            self.goal_achieved = True
                            return {
                                "thought_process": f"Collected data from {len(self.sources_visited)} sources. Average calculated from {len(all_prices)} prices.",
                                "reasoning": "Sufficient data gathered from multiple sources to calculate average.",
                                "action": {"name": "finish", "params": {"summary": self.memory.get_summary()}},
                                "is_goal_achieved": True
                            }
        
        # Phase 1: Initial search on Google
        if "google" in current_url.lower() or current_url == "" or "google.com" in current_url:
            search_input = self.find_search_input(page_state)
            if search_input:
                # Use first search query from the list
                search_query = goal_analysis["search_queries"][0] if goal_analysis["search_queries"] else goal_analysis["topic"]
                self.research_phase = "searching"
                return {
                    "thought_process": f"Starting comprehensive research. Searching Google for: {search_query}",
                    "reasoning": f"Beginning multi-source research. Will visit multiple sources to gather structured data.",
                    "action": {
                        "name": "type",
                        "params": {
                            "selector": search_input,
                            "text": search_query,
                            "press_enter": True
                        }
                    },
                    "is_goal_achieved": False
                }
        
        # Phase 2: On search results page - collect links to visit
        if "google.com/search" in current_url.lower() or "bing.com/search" in current_url.lower():
            # Find and prioritize links to visit
            relevant_links = []
            for element in elements:
                if element.get("tag") == "a" and element.get("text", ""):
                    if self.should_visit_link(element, goal_analysis):
                        element_id = element.get("id", "")
                        if element_id:
                            relevant_links.append({
                                "selector": f"#{element_id}",
                                "text": element.get("text", ""),
                                "priority": 1 if self.is_trusted_source(element.get("href", "")) else 2
                            })
            
            # Sort by priority (trusted sources first)
            relevant_links.sort(key=lambda x: x["priority"])
            
            if relevant_links and len(self.sources_visited) < self.min_sources:
                next_link = relevant_links[0]
                self.research_phase = "collecting"
                return {
                    "thought_process": f"Found relevant source: {next_link['text'][:50]}. Visiting to collect structured data.",
                    "reasoning": f"Visiting source {len(self.sources_visited) + 1} of {self.min_sources} minimum. Collecting comprehensive data.",
                    "action": {
                        "name": "click",
                        "params": {
                            "selector": next_link["selector"]
                        }
                    },
                    "is_goal_achieved": False
                }
            elif len(self.sources_visited) >= self.min_sources:
                # Have enough sources, can finish
                return {
                    "thought_process": f"Collected data from {len(self.sources_visited)} sources. Consolidating results.",
                    "reasoning": "Sufficient sources visited. Ready to consolidate data.",
                    "action": {"name": "finish", "params": {"summary": self.memory.get_summary()}},
                    "is_goal_achieved": True
                }
            else:
                # Scroll to find more links
                return {
                    "thought_process": "Scrolling search results to find more relevant sources.",
                    "reasoning": "Need more sources. Scrolling to reveal additional search results.",
                    "action": {
                        "name": "scroll",
                        "params": {
                            "direction": "down"
                        }
                    },
                    "is_goal_achieved": False
                }
        
        # Phase 3: On a content page - extract data and then look for more sources
        if self.should_extract_data(page_state):
            # Already extracted above, now decide next action
            if len(self.sources_visited) < self.min_sources:
                # Go back to search to find more sources
                return {
                    "thought_process": f"Data extracted from current source. Need {self.min_sources - len(self.sources_visited)} more sources. Returning to search.",
                    "reasoning": "Continuing multi-source research. Going back to search for more sources.",
                    "action": {
                        "name": "goto",
                        "params": {
                            "url": "https://www.google.com/search?q=" + goal_analysis["search_queries"][min(len(self.sources_visited), len(goal_analysis["search_queries"])-1)]
                        }
                    },
                    "is_goal_achieved": False
                }
            else:
                # Have enough sources
                return {
                    "thought_process": f"Collected comprehensive data from {len(self.sources_visited)} sources. Consolidating results.",
                    "reasoning": "Sufficient sources visited. Ready to consolidate structured data.",
                    "action": {"name": "finish", "params": {"summary": self.memory.get_summary()}},
                    "is_goal_achieved": True
                }
        
        # Phase 4: On any page - look for relevant links or scroll
        if any(keyword in visible_text for keyword in goal_analysis["keywords"]):
            # Look for links to other relevant pages
            relevant_links = []
            for element in elements:
                if element.get("tag") == "a" and element.get("text", ""):
                    if self.should_visit_link(element, goal_analysis):
                        element_id = element.get("id", "")
                        if element_id:
                            relevant_links.append(f"#{element_id}")
            
            if relevant_links and len(self.sources_visited) < self.min_sources:
                return {
                    "thought_process": f"Found relevant link on page. Following to collect more data.",
                    "reasoning": f"Following link to expand data collection from additional source.",
                    "action": {
                        "name": "click",
                        "params": {
                            "selector": relevant_links[0]
                        }
                    },
                    "is_goal_achieved": False
                }
            else:
                return {
                    "thought_process": "Relevant content found. Scrolling to find more information or links.",
                    "reasoning": "Scrolling to reveal more content or navigation options.",
                    "action": {
                        "name": "scroll",
                        "params": {
                            "direction": "down"
                        }
                    },
                    "is_goal_achieved": False
                }
        
        # Default: scroll or go back to search
        if len(self.sources_visited) < self.min_sources:
            return {
                "thought_process": "No clear action. Returning to search to find more sources.",
                "reasoning": f"Need more sources ({self.min_sources - len(self.sources_visited)} remaining). Going back to search.",
                "action": {
                    "name": "goto",
                    "params": {
                        "url": "https://www.google.com"
                    }
                },
                "is_goal_achieved": False
            }
        
        return {
            "thought_process": "Scrolling to reveal more content.",
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
