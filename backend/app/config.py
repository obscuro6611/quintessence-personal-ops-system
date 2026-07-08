from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    QUINT_USER: str = "reme"
    QUINT_PASSWORD: str = "quintessence-local"
    SECRET_KEY: str = "change-me-development-secret"
    DATABASE_URL: str = "sqlite:///./data/quintessence.db"
    STORAGE_DIR: str = "./storage"
    CORS_ORIGINS: str = "http://localhost:5173"

settings = Settings()
