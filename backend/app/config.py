import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Ghost Networks API"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://ghost:ghost_secret@postgres:5432/ghost_networks")
    APIFY_API_TOKEN: str = os.getenv("APIFY_API_TOKEN", "")
    AUTO_SEED: bool = os.getenv("AUTO_SEED", "true").lower() in ("true", "1", "yes")
    CORS_ORIGINS: str = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000,http://127.0.0.1:5173")

    class Config:
        case_sensitive = True

settings = Settings()
