import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Catálogo Web API"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/catalogo_db")
    JWT_SECRET: str = os.getenv("JWT_SECRET", "super-secret-key-change-in-production")
    N8N_SECRET: str = os.getenv("N8N_SECRET", "super-secret-key-change-in-production-n8n")
    MP_ACCESS_TOKEN: str = os.getenv("MP_ACCESS_TOKEN", "APP_USR-COLOCA-TU-TOKEN-DE-PRODUCCION")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # 7 días para la app móvil
    DEBUG: bool = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")
    N8N_RECOVER_PASSWORD_WEBHOOK: str = os.getenv(
        "N8N_RECOVER_PASSWORD_WEBHOOK", 
        "https://n8n.raizdigital.com.ar/webhook/recuperar-contrasena"
    )

    class Config:
        env_file = ".env"

settings = Settings()
