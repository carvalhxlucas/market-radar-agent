"""Unit tests for MissionRepository."""
import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from repositories.mission_repository import MissionRepository
from core.exceptions import MissionNotFoundError


class TestMissionRepository:
    """Test suite for MissionRepository."""
    
    def test_create_mission(self, mission_repository):
        """Test creating a new mission."""
        mission_id = mission_repository.create(
            goal="Test goal",
            headless=True,
            max_iterations=50
        )
        
        assert mission_id is not None
        assert len(mission_id) > 0
        assert mission_repository.exists(mission_id)
    
    def test_get_mission(self, mission_repository):
        """Test getting a mission by ID."""
        mission_id = mission_repository.create(
            goal="Test goal",
            headless=True,
            max_iterations=50
        )
        
        mission = mission_repository.get(mission_id)
        
        assert mission["mission_id"] == mission_id
        assert mission["goal"] == "Test goal"
        assert mission["headless"] is True
        assert mission["max_iterations"] == 50
    
    def test_get_nonexistent_mission(self, mission_repository):
        """Test getting a non-existent mission raises error."""
        with pytest.raises(MissionNotFoundError):
            mission_repository.get("nonexistent-id")
    
    def test_update_mission(self, mission_repository):
        """Test updating mission data."""
        mission_id = mission_repository.create(
            goal="Test goal",
            headless=True,
            max_iterations=50
        )
        
        mission_repository.update(mission_id, is_running=True, sources_visited=3)
        
        mission = mission_repository.get(mission_id)
        assert mission["is_running"] is True
        assert mission["sources_visited"] == 3
    
    def test_delete_mission(self, mission_repository):
        """Test deleting a mission."""
        mission_id = mission_repository.create(
            goal="Test goal",
            headless=True,
            max_iterations=50
        )
        
        assert mission_repository.exists(mission_id)
        
        mission_repository.delete(mission_id)
        
        assert not mission_repository.exists(mission_id)
        with pytest.raises(MissionNotFoundError):
            mission_repository.get(mission_id)
    
    def test_get_status(self, mission_repository):
        """Test getting mission status."""
        mission_id = mission_repository.create(
            goal="Test goal",
            headless=True,
            max_iterations=50
        )
        
        status = mission_repository.get_status(mission_id)
        
        assert status.mission_id == mission_id
        assert status.goal == "Test goal"
        assert status.is_running is False
        assert status.is_complete is False
    
    def test_exists(self, mission_repository):
        """Test checking if mission exists."""
        mission_id = mission_repository.create(
            goal="Test goal",
            headless=True,
            max_iterations=50
        )
        
        assert mission_repository.exists(mission_id)
        assert not mission_repository.exists("nonexistent-id")
