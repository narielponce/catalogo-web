from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from app.db.database import get_db
from app.models import Comercio, Producto
from app.schemas.public import ComercioPublic, ProductoPublic

router = APIRouter(prefix="/public", tags=["Vistas Públicas"])

@router.get("/comercios/{slug}", response_model=ComercioPublic)
async def get_comercio_by_slug(slug: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Comercio).filter(Comercio.slug == slug, Comercio.activo == True))
    comercio = result.scalars().first()
    if not comercio:
        raise HTTPException(status_code=404, detail="Catálogo no encontrado o inactivo")
    return comercio

@router.get("/comercios/{slug}/productos", response_model=List[ProductoPublic])
async def get_productos_by_slug(slug: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Comercio).filter(Comercio.slug == slug, Comercio.activo == True))
    comercio = result.scalars().first()
    if not comercio:
        raise HTTPException(status_code=404, detail="Catálogo no encontrado o inactivo")
        
    result_productos = await db.execute(
        select(Producto).filter(Producto.comercio_id == comercio.id, Producto.disponible == True)
    )
    return result_productos.scalars().all()
