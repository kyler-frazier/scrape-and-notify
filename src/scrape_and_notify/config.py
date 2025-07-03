"""
Configuration module for the web scraper.
"""

import logging
from pathlib import Path
from typing import Any

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)

_LOAD_SECRET = {"json_schema_extra": {"is_secret": True}}


class BaseSettingsAndSecrets(BaseSettings):
    """Base settings class with secrets."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore")

    def model_post_init(self, __context: Any) -> None:
        """Automatically read secrets for fields marked with json_schema_extra."""
        for field_name, field_info in type(self).model_fields.items():
            if field_info.json_schema_extra and field_info.json_schema_extra.get("is_secret"):
                secret_value = self._read_secret(field_name)
                setattr(self, field_name, secret_value)
                logger.debug(f"Loaded secret for field '{field_name}' from Docker secrets")

    def _read_secret(self, secret_name: str) -> str | None:
        """
        Read a secret from Docker secrets or return None if not found.
        Docker secrets are mounted at /run/secrets/<secret_name>
        """
        secret_path = Path(f"/run/secrets/{secret_name}")
        if secret_path.exists():
            try:
                return secret_path.read_text().strip()
            except Exception:
                logger.exception(f"Failed to read secret {secret_name}")
        return None


class Config(BaseSettingsAndSecrets):
    """Configuration class to manage all settings using Pydantic."""

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

    # Logging settings
    log_level: str = Field(default="INFO", description="Logging level", alias="LOG_LEVEL")

    # Discord settings - using json_schema_extra to add secret metadata
    discord_bot_token: str | None = Field(default=None, description="Discord bot token", **_LOAD_SECRET)
    discord_channel_id: str | None = Field(default=None, description="Discord channel ID", **_LOAD_SECRET)

    @field_validator("search_type")
    @classmethod
    def validate_search_type(cls, v: str) -> str:
        """Normalize search_type to lowercase."""
        return v.lower()

    @property
    def log_level_int(self) -> int:
        """Convert log level string to integer."""
        return getattr(logging, self.log_level.upper())
