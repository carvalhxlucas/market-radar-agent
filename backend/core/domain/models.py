"""Domain models for MarketRadar."""
from datetime import datetime
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class PriceData(BaseModel):
    """Price data model."""
    value: float = Field(..., description="Price value")
    currency: str = Field(default="BRL", description="Currency code")
    raw: Optional[str] = Field(None, description="Raw price string")


class ExtractedData(BaseModel):
    """Extracted data model."""
    prices: Optional[List[PriceData]] = Field(None, description="List of prices")
    product_names: Optional[List[str]] = Field(None, description="List of product names")
    url: Optional[str] = Field(None, description="Source URL")
    title: Optional[str] = Field(None, description="Page title")
    description: Optional[str] = Field(None, description="Page description")
    specifications: Optional[Dict[str, str]] = Field(None, description="Product specifications")
    timestamp: datetime = Field(default_factory=datetime.now, description="Extraction timestamp")
    average_price: Optional[float] = Field(None, description="Calculated average price")


class ActionHistory(BaseModel):
    """Action history model."""
    timestamp: datetime = Field(default_factory=datetime.now)
    action: str = Field(..., description="Action name")
    params: Dict[str, Any] = Field(..., description="Action parameters")
    url: str = Field(..., description="URL where action was performed")
    result: str = Field(default="", description="Action result")


class MissionStatus(BaseModel):
    """Mission status model."""
    mission_id: str = Field(..., description="Mission identifier")
    goal: str = Field(..., description="Mission goal")
    is_running: bool = Field(default=False, description="Whether mission is running")
    is_complete: bool = Field(default=False, description="Whether mission is complete")
    error: Optional[str] = Field(None, description="Error message if any")
    sources_visited: int = Field(default=0, description="Number of sources visited")
    data_points: int = Field(default=0, description="Number of data points extracted")


class GoalAnalysis(BaseModel):
    """Goal analysis model."""
    type: str = Field(..., description="Research type")
    keywords: List[str] = Field(default_factory=list, description="Extracted keywords")
    target_data: List[str] = Field(default_factory=list, description="Target data types")
    search_queries: List[str] = Field(default_factory=list, description="Search queries")
    topic: str = Field(default="", description="Main topic")
