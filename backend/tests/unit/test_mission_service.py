"""Unit tests for MissionService."""
import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from services.mission_service import MissionService
from repositories.mission_repository import MissionRepository
from core.exceptions import MissionNotFoundError, MissionAlreadyRunningError


class TestMissionService:
    """Test suite for MissionService."""
    
    def test_create_mission(self, mission_service):
        """Test creating a new mission."""
        result = mission_service.create_mission(
            goal="Test goal",
            headless=True,
            max_iterations=50
        )
        
        assert "mission_id" in result
        assert "websocket_url" in result
        assert result["mission_id"] is not None
        assert "ws://" in result["websocket_url"]
    
    def test_get_mission_status(self, mission_service):
        """Test getting mission status."""
        result = mission_service.create_mission(
            goal="Test goal",
            headless=True,
            max_iterations=50
        )
        mission_id = result["mission_id"]
        
        status = mission_service.get_mission_status(mission_id)
        
        assert status.mission_id == mission_id
        assert status.goal == "Test goal"
        assert status.is_running is False
    
    def test_get_nonexistent_mission_status(self, mission_service):
        """Test getting status of non-existent mission."""
        with pytest.raises(MissionNotFoundError):
            mission_service.get_mission_status("nonexistent-id")
    
    def test_get_message_queue(self, mission_service):
        """Test getting message queue for mission."""
        result = mission_service.create_mission(
            goal="Test goal",
            headless=True,
            max_iterations=50
        )
        mission_id = result["mission_id"]
        
        queue = mission_service.get_message_queue(mission_id)
        
        assert queue is not None
    
    def test_stop_mission(self, mission_service):
        """Test stopping a mission."""
        result = mission_service.create_mission(
            goal="Test goal",
            headless=True,
            max_iterations=50
        )
        mission_id = result["mission_id"]
        
        # Update mission to running state
        mission_service.repository.update(mission_id, is_running=True)
        
        mission_service.stop_mission(mission_id)
        
        mission = mission_service.repository.get(mission_id)
        assert mission["is_running"] is False
    
    def test_delete_mission(self, mission_service):
        """Test deleting a mission."""
        result = mission_service.create_mission(
            goal="Test goal",
            headless=True,
            max_iterations=50
        )
        mission_id = result["mission_id"]
        
        assert mission_service.repository.exists(mission_id)
        
        mission_service.delete_mission(mission_id)
        
        assert not mission_service.repository.exists(mission_id)
