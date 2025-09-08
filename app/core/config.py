from pydantic_settings import BaseSettings
from pydantic import ConfigDict, Field
from typing import List, Optional
import json

class Settings(BaseSettings):
    APP_URL: str
    APP_FRONTEND_URL: str
    SALEOR_API_URL: str
    REDIS_URL: str = "redis://127.0.0.1:6379/0"
    CORS_ORIGINS: str = "http://127.0.0.1:3000,https://your-instance.saleor.cloud"
    SALEOR_APP_TOKEN: str = ""  # Токен для авторизации в Saleor
    
    # Additional settings that may be present in .env but not used by our app
    APPLICATION_HOST: str = "0.0.0.0"
    APPLICATION_PORT: int = 8000
    APPLICATION_PORT_FRONTEND: int = 3000
    DEBUG: bool = True
    RELOAD: bool = True
    
    def get_cors_origins(self) -> List[str]:
        """Parse CORS_ORIGINS string into list"""
        if isinstance(self.CORS_ORIGINS, str):
            # Try JSON format first
            if self.CORS_ORIGINS.startswith('[') and self.CORS_ORIGINS.endswith(']'):
                try:
                    return json.loads(self.CORS_ORIGINS)
                except json.JSONDecodeError:
                    pass
            # Try comma-separated format
            if ',' in self.CORS_ORIGINS:
                return [origin.strip() for origin in self.CORS_ORIGINS.split(',')]
            # Single origin
            return [self.CORS_ORIGINS.strip()]
        return []

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"  # Ignore extra fields instead of raising validation errors
    )

settings = Settings()
