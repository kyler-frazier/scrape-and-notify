"""
Configuration module for the web scraper.
"""

import logging

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    """Configuration class to manage all settings using Pydantic."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore")

    # Scraper settings
    target_url: str = Field(description="The target URL to scrape", alias="TARGET_URL")

    # Search configuration
    negative: bool = Field(default=False, description="If True, search for the absence of a match", alias="NEGATIVE")
    search_type: str = Field(default="json", description="Search type: 'html' or 'json'", alias="SEARCH_TYPE")
    target_match: str = Field(description="Target value to match", alias="TARGET_MATCH")
    target_location: str | None = Field(description="JSONPath location for target match", alias="TARGET_LOCATION")

    check_interval: int = Field(
        default=900, description="Check interval in seconds (default: 15 minutes)", alias="CHECK_INTERVAL"
    )

    # Request settings
    request_timeout: int = Field(default=30, description="Request timeout in seconds", alias="REQUEST_TIMEOUT")
    request_delay: float = Field(default=1.0, description="Delay between requests in seconds", alias="REQUEST_DELAY")

    # Discord settings
    discord_bot_token: str | None = Field(
        default=None, description="Discord bot token for notifications", alias="DISCORD_BOT_TOKEN"
    )
    discord_channel_id: str | None = Field(
        default=None, description="Discord channel ID for notifications", alias="DISCORD_CHANNEL_ID"
    )

    # Logging settings
    log_level: str = Field(default="INFO", description="Logging level", alias="LOG_LEVEL")

    @field_validator("search_type")
    @classmethod
    def validate_search_type(cls, v: str) -> str:
        """Normalize search_type to lowercase."""
        return v.lower()

    @property
    def log_level_int(self) -> int:
        """Convert log level string to integer."""
        return getattr(logging, self.log_level.upper())
