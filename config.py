import os
from typing import Optional

class Config:
    # OpenRouter API configuration
    OPENROUTER_API_KEY: Optional[str] = os.getenv("OPENROUTER_API_KEY")
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    
    # LLM Model selection (using a good general model)
    DEFAULT_MODEL: str = "anthropic/claude-3.5-sonnet"
    
    # API settings
    REQUEST_TIMEOUT: int = 30
    MAX_TRANSCRIPT_LENGTH: int = 50000  # characters
    
    @classmethod
    def validate_config(cls) -> bool:
        """Validate that required configuration is present"""
        if not cls.OPENROUTER_API_KEY:
            return False
        return True