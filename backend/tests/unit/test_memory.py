"""Unit tests for Memory."""
import pytest
from datetime import datetime
from infrastructure.memory import Memory


class TestMemory:
    """Test suite for Memory."""
    
    def test_add_action(self, memory):
        """Test adding an action to history."""
        memory.add_action("goto", {"url": "https://example.com"}, "https://example.com", "success")
        
        assert len(memory.history) == 1
        assert memory.history[0].action == "goto"
        assert memory.history[0].url == "https://example.com"
    
    def test_is_loop_detected(self, memory):
        """Test loop detection."""
        url = "https://example.com"
        
        # Add action 3 times (threshold)
        for _ in range(3):
            memory.add_action("goto", {"url": url}, url, "success")
        
        assert memory.is_loop_detected(url) is True
        assert memory.is_loop_detected("https://other.com") is False
    
    def test_get_recent_actions(self, memory):
        """Test getting recent actions."""
        # Add 5 actions
        for i in range(5):
            memory.add_action("action", {"param": i}, f"https://example.com/{i}", "success")
        
        recent = memory.get_recent_actions(3)
        
        assert len(recent) == 3
        assert recent[0].action == "action"
    
    def test_add_extracted_data(self, memory, sample_extracted_data):
        """Test adding extracted data."""
        memory.add_extracted_data(sample_extracted_data)
        
        assert len(memory.get_extracted_data()) == 1
        data = memory.get_extracted_data()[0]
        assert "prices" in data
        assert "timestamp" in data
    
    def test_get_extracted_data(self, memory, sample_extracted_data):
        """Test getting extracted data."""
        memory.add_extracted_data(sample_extracted_data)
        memory.add_extracted_data({"url": "https://example.com/2"})
        
        data = memory.get_extracted_data()
        
        assert len(data) == 2
        assert data[0]["prices"] == sample_extracted_data["prices"]
    
    def test_get_summary(self, memory, sample_extracted_data):
        """Test getting mission summary."""
        memory.add_action("goto", {"url": "https://example.com"}, "https://example.com", "success")
        memory.add_extracted_data(sample_extracted_data)
        
        summary = memory.get_summary()
        
        assert "Research Summary" in summary
        assert "Total actions: 1" in summary
        assert "Extracted data points: 1" in summary
        assert "Sources visited" in summary
