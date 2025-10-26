import os
from typing import Optional
from pydantic import validator
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # OpenRouter API configuration
    OPENROUTER_API_KEY: Optional[str] = None
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"

    # LLM Model selection (using a good general model)
    DEFAULT_MODEL: str = "anthropic/claude-3.5-sonnet"

    # API settings
    REQUEST_TIMEOUT: int = 240
    MAX_TRANSCRIPT_LENGTH: int = 50000  # characters

    # Deployment configuration
    BASE_PATH: str = ""

    @validator('BASE_PATH')
    def validate_base_path(cls, v):
        if v:  # Only validate if the string is not empty
            if not v.startswith('/'):
                raise ValueError('BASE_PATH must start with a "/"')
            if v.endswith('/'):
                raise ValueError('BASE_PATH must not end with a "/"')
        return v

    def get_base_path(self) -> str:
        """Get the base path for URL construction"""
        return self.BASE_PATH

    def validate_config(self) -> bool:
        """Validate that required configuration is present"""
        if not self.OPENROUTER_API_KEY:
            return False
        return True

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'

# Create a single, validated instance of the settings that can be imported by other modules.
# This instance is named 'Config' for backward compatibility with existing imports.
Config = Settings()