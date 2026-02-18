"""Application settings and configuration."""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application configuration settings."""
    
    # API Settings
    api_title: str = "MarketRadar API"
    api_version: str = "1.0.0"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_reload: bool = False
    
    # CORS Settings
    cors_origins: List[str] = ["*"]
    cors_allow_credentials: bool = True
    cors_allow_methods: List[str] = ["*"]
    cors_allow_headers: List[str] = ["*"]
    
    # Browser Settings
    browser_headless: bool = True
    browser_timeout: int = 30000
    browser_viewport_width: int = 1920
    browser_viewport_height: int = 1080
    
    # Agent Settings
    agent_max_iterations: int = 100
    agent_min_sources: int = 5
    agent_loop_threshold: int = 3
    
    # Trusted Sources
    trusted_domains: List[str] = [
        "wikipedia.org",
        "mercadolivre.com.br",
        "amazon.com.br",
        "magazineluiza.com.br",
        "americanas.com.br",
        "casasbahia.com.br",
        "extra.com.br",
        "submarino.com.br",
        "shoptime.com.br",
        "pontofrio.com.br",
        "buscape.com.br",
        "zoom.com.br",
        "compare.com.br",
        "preco.com.br",
        "google.com/shopping",
        "bing.com/shop"
    ]
    
    # Skip Domains
    skip_domains: List[str] = [
        "google.com",
        "bing.com",
        "duckduckgo.com",
        "facebook.com",
        "twitter.com",
        "instagram.com"
    ]
    
    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
