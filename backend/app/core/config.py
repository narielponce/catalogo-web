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

import json

def get_config_path():
    if os.path.exists("/app/uploads"):
        return "/app/uploads/config.json"
    os.makedirs("./uploads", exist_ok=True)
    return "./uploads/config.json"

def get_subscription_price() -> float:
    try:
        path = get_config_path()
        if os.path.exists(path):
            with open(path, "r") as f:
                data = json.load(f)
                return float(data.get("monto_suscripcion", 1000.00))
    except Exception as e:
        print(f"Error reading config: {e}")
    return 1000.00

def set_subscription_price(price: float):
    try:
        path = get_config_path()
        os.makedirs(os.path.dirname(path), exist_ok=True)
        data = {}
        if os.path.exists(path):
            with open(path, "r") as f:
                data = json.load(f)
        data["monto_suscripcion"] = price
        with open(path, "w") as f:
            json.dump(data, f)
    except Exception as e:
        print(f"Error writing config: {e}")
