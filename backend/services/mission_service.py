"""Service for mission management."""
from typing import Dict, Any, Optional
from core.exceptions import MissionAlreadyRunningError, MissionNotFoundError
from repositories.mission_repository import MissionRepository
from core.domain.models import MissionStatus
import queue
import threading


class MissionService:
    """Service for managing missions."""
    
    def __init__(self, mission_repository: MissionRepository):
        """
        Initialize mission service.
        
        Args:
            mission_repository: Repository for mission data
        """
        self.repository = mission_repository
        self._active_threads: Dict[str, threading.Thread] = {}
        self._message_queues: Dict[str, queue.Queue] = {}
    
    def create_mission(
        self,
        goal: str,
        headless: bool = True,
        max_iterations: int = 100
    ) -> Dict[str, str]:
        """
        Create a new mission.
        
        Args:
            goal: Mission goal
            headless: Whether to run browser in headless mode
            max_iterations: Maximum number of iterations
            
        Returns:
            Dictionary with mission_id and websocket_url
        """
        mission_id = self.repository.create(goal, headless, max_iterations)
        message_queue = queue.Queue()
        self._message_queues[mission_id] = message_queue
        
        return {
            "mission_id": mission_id,
            "websocket_url": f"ws://localhost:8000/ws/{mission_id}"
        }
    
    def get_mission_status(self, mission_id: str) -> MissionStatus:
        """
        Get mission status.
        
        Args:
            mission_id: Mission identifier
            
        Returns:
            MissionStatus object
            
        Raises:
            MissionNotFoundError: If mission not found
        """
        return self.repository.get_status(mission_id)
    
    def start_mission_thread(
        self,
        mission_id: str,
        run_function,
        *args
    ) -> None:
        """
        Start mission in a separate thread.
        
        Args:
            mission_id: Mission identifier
            run_function: Function to run in thread
            *args: Arguments for run_function
            
        Raises:
            MissionNotFoundError: If mission not found
            MissionAlreadyRunningError: If mission already running
        """
        mission = self.repository.get(mission_id)
        
        if mission["is_running"]:
            raise MissionAlreadyRunningError(f"Mission {mission_id} is already running")
        
        self.repository.update(mission_id, is_running=True)
        
        thread = threading.Thread(
            target=run_function,
            args=(mission_id, *args),
            daemon=True
        )
        self._active_threads[mission_id] = thread
        thread.start()
    
    def stop_mission(self, mission_id: str) -> None:
        """
        Stop a running mission.
        
        Args:
            mission_id: Mission identifier
            
        Raises:
            MissionNotFoundError: If mission not found
        """
        mission = self.repository.get(mission_id)
        self.repository.update(mission_id, is_running=False)
        
        if mission_id in self._active_threads:
            # Thread will stop on next iteration check
            pass
    
    def get_message_queue(self, mission_id: str) -> queue.Queue:
        """
        Get message queue for mission.
        
        Args:
            mission_id: Mission identifier
            
        Returns:
            Message queue
            
        Raises:
            MissionNotFoundError: If mission not found
        """
        if mission_id not in self._message_queues:
            raise MissionNotFoundError(f"Mission {mission_id} not found")
        return self._message_queues[mission_id]
    
    def delete_mission(self, mission_id: str) -> None:
        """
        Delete mission and cleanup resources.
        
        Args:
            mission_id: Mission identifier
        """
        if mission_id in self._active_threads:
            del self._active_threads[mission_id]
        if mission_id in self._message_queues:
            del self._message_queues[mission_id]
        self.repository.delete(mission_id)
