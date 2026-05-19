from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import logging
import os

from app.core.config import settings
from app.db.database import get_db, engine
from app.models import Base
from app.api.auth import router as auth_router
from app.api.productos import router as productos_router
from app.api.public import router as public_router
from app.api.superadmin import router as superadmin_router
from app.api.n8n import router as n8n_router

logger = logging.getLogger(__name__)

# Lifespan events de FastAPI (recomendado sobre eventos startup/shutdown)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # En desarrollo, esto crea las tablas automáticamente.
    # TODO: Para producción y evolución real del esquema, usaremos Alembic (migraciones)
    try:
        async with engine.begin() as conn:
            # Crea todas las tablas definidas en models.py si no existen
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Tablas de base de datos validadas/creadas con éxito.")
    except Exception as e:
        logger.error(f"Error al conectar con la base de datos durante startup: {e}")
    
    yield
    
    # Clean up al detener la app
    await engine.dispose()

app = FastAPI(
    title=settings.PROJECT_NAME,
    lifespan=lifespan
)

app.include_router(auth_router)
app.include_router(productos_router)
app.include_router(public_router)
app.include_router(superadmin_router)
app.include_router(n8n_router)

# Crear directorio si no existe (seguridad extra)
os.makedirs("/app/uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="/app/uploads"), name="uploads")

@app.get("/")
def root():
    return {"message": f"Bienvenido a {settings.PROJECT_NAME}"}

@app.get("/health", summary="Chequeo de estado de la API y DB")
async def health_check(db: AsyncSession = Depends(get_db)):
    """Endpoint para verificar que el backend y la base de datos estén funcionando correctamente."""
    try:
        # Ejecutar una consulta ultra simple
        result = await db.execute(text("SELECT 1"))
        if result.scalar() == 1:
            return {"status": "ok", "database": "connected"}
        raise Exception("Fallo en la verificación de DB")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
