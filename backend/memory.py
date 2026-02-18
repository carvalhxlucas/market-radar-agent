from typing import List, Dict, Any
from datetime import datetime
from pydantic import BaseModel


class ActionHistory(BaseModel):
    timestamp: datetime
    action: str
    params: Dict[str, Any]
    url: str
    result: str


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
        return self.history[-count:] if len(self.history) > count else self.history
    
    def add_extracted_data(self, data: Dict[str, Any]):
        self.extracted_data.append({
            **data,
            "timestamp": datetime.now().isoformat()
        })
    
    def get_extracted_data(self) -> List[Dict[str, Any]]:
        return self.extracted_data
    
    def get_summary(self) -> str:
        recent = self.get_recent_actions(5)
        summary = f"Total actions: {len(self.history)}\n"
        summary += f"Extracted data points: {len(self.extracted_data)}\n"
        summary += "Recent actions:\n"
        for action in recent:
            summary += f"  - {action.action} on {action.url}\n"
        return summary
