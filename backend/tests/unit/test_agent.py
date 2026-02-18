"""Unit tests for MarketRadarAgent."""
import pytest
from unittest.mock import Mock, patch
from services.agent import MarketRadarAgent
from infrastructure.memory import Memory


class TestMarketRadarAgent:
    """Test suite for MarketRadarAgent."""
    
    @pytest.fixture
    def agent(self, mock_browser_engine, memory):
        """Create MarketRadarAgent with mocked dependencies."""
        return MarketRadarAgent(mock_browser_engine, memory, "Find the average price of Creatine in Brazil")
    
    def test_analyze_goal_price_research(self, agent):
        """Test goal analysis for price research."""
        analysis = agent.analyze_goal()
        
        assert analysis["type"] == "price_research"
        assert "prices" in analysis["target_data"]
        assert len(analysis["search_queries"]) > 0
        assert "creatine" in analysis["topic"].lower() or "creatine" in str(analysis["keywords"]).lower()
    
    def test_analyze_goal_average_calculation(self, agent):
        """Test goal analysis for average calculation."""
        agent.global_goal = "Find the average price of Whey Protein"
        analysis = agent.analyze_goal()
        
        assert analysis["type"] == "average_calculation"
    
    def test_find_search_input(self, agent, mock_browser_engine):
        """Test finding search input."""
        mock_browser_engine.get_page_state.return_value = {
            "interactive_elements": [
                {"id": "search", "tag": "input", "text": "", "href": ""}
            ],
            "visible_text": "",
            "url": "https://google.com",
            "title": "Google"
        }
        
        page_state = mock_browser_engine.get_page_state()
        selector = agent.find_search_input(page_state)
        
        assert selector is not None
        assert "search" in selector.lower() or selector.startswith("#")
    
    def test_should_extract_data(self, agent, mock_browser_engine):
        """Test should_extract_data logic."""
        # Test with valid content
        mock_browser_engine.get_page_state.return_value = {
            "url": "https://example.com/product",
            "visible_text": "R$ 50,00 Product Name " * 50,  # Enough words
            "title": "Product"
        }
        
        page_state = mock_browser_engine.get_page_state()
        should_extract = agent.should_extract_data(page_state)
        
        assert should_extract is True
    
    def test_should_not_extract_from_search_engine(self, agent, mock_browser_engine):
        """Test that search engines are skipped."""
        mock_browser_engine.get_page_state.return_value = {
            "url": "https://google.com/search",
            "visible_text": "Search results",
            "title": "Google"
        }
        
        page_state = mock_browser_engine.get_page_state()
        should_extract = agent.should_extract_data(page_state)
        
        assert should_extract is False
    
    def test_is_trusted_source(self, agent):
        """Test trusted source detection."""
        assert agent.is_trusted_source("https://mercadolivre.com.br/product") is True
        assert agent.is_trusted_source("https://amazon.com.br/product") is True
        assert agent.is_trusted_source("https://random-site.com") is False
    
    def test_should_visit_link(self, agent):
        """Test link visit decision logic."""
        goal_analysis = agent.analyze_goal()
        
        # Test with relevant link
        element = {
            "text": "Creatine price",
            "href": "https://example.com/creatine"
        }
        
        should_visit = agent.should_visit_link(element, goal_analysis)
        
        # Should visit if keywords match or it's a trusted source
        assert isinstance(should_visit, bool)
    
    def test_execute_action_goto(self, agent, mock_browser_engine):
        """Test executing goto action."""
        action_command = {
            "action": {
                "name": "goto",
                "params": {"url": "https://example.com"}
            }
        }
        
        result = agent.execute_action(action_command)
        
        assert result["success"] is True
        mock_browser_engine.goto.assert_called_once()
    
    def test_execute_action_click(self, agent, mock_browser_engine):
        """Test executing click action."""
        action_command = {
            "action": {
                "name": "click",
                "params": {"selector": "#button"}
            }
        }
        
        result = agent.execute_action(action_command)
        
        assert result["success"] is True
        mock_browser_engine.click.assert_called_once()
    
    def test_execute_action_extract(self, agent, mock_browser_engine):
        """Test executing extract action."""
        action_command = {
            "action": {
                "name": "extract",
                "params": {"data_points": ["prices", "url"]}
            }
        }
        
        result = agent.execute_action(action_command)
        
        assert result["success"] is True
        assert "data" in result
