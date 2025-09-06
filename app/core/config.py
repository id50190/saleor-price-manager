from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_URL: str
    APP_FRONTEND_URL: str
    SALEOR_API_URL: str
    REDIS_URL: str = "redis://localhost:6379/0"
    CORS_ORIGINS: list = []
    SALEOR_APP_TOKEN: str = ""  # Токен для авторизации в Saleor
    
    # Additional settings that may be present in .env but not used by our app
    APPLICATION_HOST: str = "0.0.0.0"
    APPLICATION_PORT: int = 8000
    APPLICATION_PORT_FRONTEND: int = 3000
    DEBUG: bool = True
    RELOAD: bool = True

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # Ignore extra fields instead of raising validation errors

settings = Settings()
