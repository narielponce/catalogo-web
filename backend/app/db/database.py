from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.core.config import settings

# Crear engine asincrónico para PostgreSQL
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    pool_pre_ping=True, # Verifica si la conexión está viva antes de usarla
    pool_size=5,        # Límite bajo ideal para VPS de 2GB
    max_overflow=10
)

# Fábrica de sesiones
async_session = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Dependencia para inyectar la sesión de DB en FastAPI
async def get_db():
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()
