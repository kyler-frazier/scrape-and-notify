"""
Configuration module for the web scraper.
"""

import logging
import os
from typing import Optional


class Config:
    """Configuration class to manage all settings."""

    # Scraper settings
    TARGET_URL: str = os.getenv("TARGET_URL", "https://prometheusapartments.com/ca/sunnyvale-apartments/ironworks")
    TARGET_TEXT: str = os.getenv("TARGET_TEXT", "2 Bed")
    CHECK_INTERVAL: int = int(os.getenv("CHECK_INTERVAL", "3600"))  # 1 hour default

    # Request settings
    REQUEST_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT", "30"))
    REQUEST_DELAY: float = float(os.getenv("REQUEST_DELAY", "1.0"))

    # Discord settings
    DISCORD_BOT_TOKEN: Optional[str] = os.getenv("DISCORD_BOT_TOKEN")
    DISCORD_CHANNEL_ID: Optional[str] = os.getenv("DISCORD_CHANNEL_ID")

    # Logging settings
    LOG_LEVEL: str = logging.getLevelName(os.getenv("LOG_LEVEL", "INFO").upper())
