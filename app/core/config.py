from pydantic import BaseSettings

class Settings(BaseSettings):
    APP_URL: str
    APP_FRONTEND_URL: str
    SALEOR_API_URL: str
    REDIS_URL: str = "redis://localhost:6379/0"
    CORS_ORIGINS: list = []
    SALEOR_APP_TOKEN: str = ""  # Токен для авторизации в Saleor

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
