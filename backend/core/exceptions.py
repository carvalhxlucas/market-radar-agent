"""Custom exceptions for MarketRadar application."""


class MarketRadarException(Exception):
    """Base exception for MarketRadar application."""
    pass


class MissionException(MarketRadarException):
    """Exception raised for mission-related errors."""
    pass


class MissionNotFoundError(MissionException):
    """Exception raised when a mission is not found."""
    pass


class MissionAlreadyRunningError(MissionException):
    """Exception raised when trying to start an already running mission."""
    pass


class BrowserException(MarketRadarException):
    """Exception raised for browser-related errors."""
    pass


class ExtractionException(MarketRadarException):
    """Exception raised for data extraction errors."""
    pass


class ConfigurationError(MarketRadarException):
    """Exception raised for configuration errors."""
    pass
