"""Pytest configuration and shared fixtures."""
import pytest
import sys
import os
from typing import Dict, Any
from unittest.mock import Mock, MagicMock

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from repositories.mission_repository import MissionRepository
from infrastructure.memory import Memory
from infrastructure.browser_engine import BrowserEngine
from services.mission_service import MissionService


@pytest.fixture
def mission_repository():
    """Fixture for MissionRepository."""
    return MissionRepository()


@pytest.fixture
def memory():
    """Fixture for Memory."""
    return Memory()


@pytest.fixture
def mock_browser_engine():
    """Fixture for mocked BrowserEngine."""
    mock = Mock(spec=BrowserEngine)
    mock.current_url = "https://www.google.com"
    mock.get_page_state.return_value = {
        "url": "https://www.google.com",
        "interactive_elements": [],
        "visible_text": "Test page content",
        "title": "Test Page"
    }
    mock.goto.return_value = {"success": True, "url": "https://www.google.com"}
    mock.click.return_value = {"success": True, "url": "https://www.google.com"}
    mock.type.return_value = {"success": True}
    mock.scroll.return_value = {"success": True}
    mock.wait.return_value = {"success": True}
    return mock


@pytest.fixture
def mission_service(mission_repository):
    """Fixture for MissionService."""
    return MissionService(mission_repository)


@pytest.fixture
def sample_mission_data() -> Dict[str, Any]:
    """Fixture for sample mission data."""
    return {
        "goal": "Find the average price of Creatine in Brazil",
        "headless": True,
        "max_iterations": 50
    }


@pytest.fixture
def sample_extracted_data() -> Dict[str, Any]:
    """Fixture for sample extracted data."""
    return {
        "prices": [
            {"value": 50.00, "currency": "BRL", "raw": "R$ 50,00"},
            {"value": 55.00, "currency": "BRL", "raw": "R$ 55,00"},
            {"value": 60.00, "currency": "BRL", "raw": "R$ 60,00"}
        ],
        "product_names": ["Creatine 300g", "Creatine Monohydrate"],
        "url": "https://example.com/product",
        "title": "Product Page"
    }
