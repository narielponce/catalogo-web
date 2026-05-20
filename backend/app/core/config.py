import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Catálogo Web API"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/catalogo_db")
    JWT_SECRET: str = os.getenv("JWT_SECRET", "super-secret-key-change-in-production")
    N8N_SECRET: str = os.getenv("N8N_SECRET", "super-secret-key-change-in-production-n8n")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # 7 días para la app móvil

    class Config:
        env_file = ".env"

settings = Settings()
