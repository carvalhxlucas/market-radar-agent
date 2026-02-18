"""Integration tests for API endpoints."""
import pytest
import sys
import os
from fastapi.testclient import TestClient

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from api.app import create_app
from repositories.mission_repository import MissionRepository
from services.mission_service import MissionService


@pytest.fixture
def client():
    """Create test client."""
    app = create_app()
    return TestClient(app)


class TestAPIEndpoints:
    """Test suite for API endpoints."""
    
    def test_root_endpoint(self, client):
        """Test root endpoint."""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "status" in data
        assert data["status"] == "running"
    
    def test_health_endpoint(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    def test_start_mission(self, client):
        """Test starting a mission."""
        response = client.post(
            "/api/v1/mission/start",
            json={
                "goal": "Find the average price of Creatine in Brazil",
                "headless": True,
                "max_iterations": 50
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "mission_id" in data
        assert "websocket_url" in data
        assert data["mission_id"] is not None
    
    def test_start_mission_invalid_data(self, client):
        """Test starting mission with invalid data."""
        response = client.post(
            "/api/v1/mission/start",
            json={
                "goal": "",  # Empty goal should fail validation
                "headless": True
            }
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_get_mission_status(self, client):
        """Test getting mission status."""
        # First create a mission
        create_response = client.post(
            "/api/v1/mission/start",
            json={
                "goal": "Test goal",
                "headless": True,
                "max_iterations": 50
            }
        )
        mission_id = create_response.json()["mission_id"]
        
        # Then get status
        response = client.get(f"/api/v1/mission/{mission_id}/status")
        
        assert response.status_code == 200
        data = response.json()
        assert data["mission_id"] == mission_id
        assert data["goal"] == "Test goal"
    
    def test_get_nonexistent_mission_status(self, client):
        """Test getting status of non-existent mission."""
        response = client.get("/api/v1/mission/nonexistent-id/status")
        
        assert response.status_code == 404
    
    def test_stop_mission(self, client):
        """Test stopping a mission."""
        # First create a mission
        create_response = client.post(
            "/api/v1/mission/start",
            json={
                "goal": "Test goal",
                "headless": True,
                "max_iterations": 50
            }
        )
        mission_id = create_response.json()["mission_id"]
        
        # Then stop it
        response = client.delete(f"/api/v1/mission/{mission_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
