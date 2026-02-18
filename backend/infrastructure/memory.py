"""Memory implementation for agent state management."""
from typing import List, Dict, Any
from datetime import datetime
from core.domain.models import ActionHistory


class Memory:
    def __init__(self):
        self.history: List[ActionHistory] = []
        self.extracted_data: List[Dict[str, Any]] = []
        self.url_visit_count: Dict[str, int] = {}
    
    def add_action(self, action: str, params: Dict[str, Any], url: str, result: str = ""):
        self.history.append(ActionHistory(
            timestamp=datetime.now(),
            action=action,
            params=params,
            url=url,
            result=result
        ))
        self.url_visit_count[url] = self.url_visit_count.get(url, 0) + 1
    
    def is_loop_detected(self, url: str) -> bool:
        return self.url_visit_count.get(url, 0) >= 3
    
    def get_recent_actions(self, count: int = 10) -> List[ActionHistory]:
        """
        Get recent actions.
        
        Args:
            count: Number of recent actions to return
            
        Returns:
            List of recent ActionHistory objects
        """
        return self.history[-count:] if len(self.history) > count else self.history
    
    def add_extracted_data(self, data: Dict[str, Any]):
        self.extracted_data.append({
            **data,
            "timestamp": datetime.now().isoformat()
        })
    
    def get_extracted_data(self) -> List[Dict[str, Any]]:
        """
        Get all extracted data.
        
        Returns:
            List of extracted data dictionaries
        """
        return self.extracted_data
    
    def get_summary(self) -> str:
        recent = self.get_recent_actions(5)
        summary = f"Research Summary\n"
        summary += f"Total actions: {len(self.history)}\n"
        summary += f"Sources visited: {len(set(d.get('url', '') for d in self.extracted_data))}\n"
        summary += f"Extracted data points: {len(self.extracted_data)}\n"
        
        # Count total prices found
        total_prices = 0
        for data in self.extracted_data:
            if "prices" in data:
                prices = data["prices"]
                total_prices += len(prices) if isinstance(prices, list) else 1
        
        if total_prices > 0:
            summary += f"Total prices found: {total_prices}\n"
        
        # List unique sources
        unique_sources = set()
        for data in self.extracted_data:
            if "url" in data and data["url"]:
                unique_sources.add(data["url"])
        
        if unique_sources:
            summary += f"\nSources consulted:\n"
            for i, source in enumerate(list(unique_sources)[:10], 1):
                summary += f"  {i}. {source}\n"
        
        summary += "\nRecent actions:\n"
        for action in recent:
            summary += f"  - {action.action} on {action.url}\n"
        
        return summary
