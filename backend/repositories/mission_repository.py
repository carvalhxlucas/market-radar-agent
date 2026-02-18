"""Repository for mission data management."""
from typing import Dict, Optional
from uuid import UUID
from core.domain.models import MissionStatus
from core.exceptions import MissionNotFoundError
import uuid


class MissionRepository:
    """Repository for managing mission data."""
    
    def __init__(self):
        """Initialize repository with in-memory storage."""
        self._missions: Dict[str, Dict] = {}
    
    def create(self, goal: str, headless: bool, max_iterations: int) -> str:
        """
        Create a new mission.
        
        Args:
            goal: Mission goal
            headless: Whether to run browser in headless mode
            max_iterations: Maximum number of iterations
            
        Returns:
            Mission ID
        """
        mission_id = str(uuid.uuid4())
        self._missions[mission_id] = {
            "mission_id": mission_id,
            "goal": goal,
            "headless": headless,
            "max_iterations": max_iterations,
            "is_running": False,
            "is_complete": False,
            "error": None,
            "sources_visited": 0,
            "data_points": 0
        }
        return mission_id
    
    def get(self, mission_id: str) -> Dict:
        """
        Get mission by ID.
        
        Args:
            mission_id: Mission identifier
            
        Returns:
            Mission data
            
        Raises:
            MissionNotFoundError: If mission not found
        """
        if mission_id not in self._missions:
            raise MissionNotFoundError(f"Mission {mission_id} not found")
        return self._missions[mission_id]
    
    def update(self, mission_id: str, **kwargs) -> None:
        """
        Update mission data.
        
        Args:
            mission_id: Mission identifier
            **kwargs: Fields to update
            
        Raises:
            MissionNotFoundError: If mission not found
        """
        mission = self.get(mission_id)
        mission.update(kwargs)
    
    def delete(self, mission_id: str) -> None:
        """
        Delete mission.
        
        Args:
            mission_id: Mission identifier
            
        Raises:
            MissionNotFoundError: If mission not found
        """
        if mission_id not in self._missions:
            raise MissionNotFoundError(f"Mission {mission_id} not found")
        del self._missions[mission_id]
    
    def get_status(self, mission_id: str) -> MissionStatus:
        """
        Get mission status.
        
        Args:
            mission_id: Mission identifier
            
        Returns:
            MissionStatus object
        """
        mission = self.get(mission_id)
        return MissionStatus(**mission)
    
    def exists(self, mission_id: str) -> bool:
        """
        Check if mission exists.
        
        Args:
            mission_id: Mission identifier
            
        Returns:
            True if exists, False otherwise
        """
        return mission_id in self._missions
