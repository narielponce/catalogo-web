from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from uuid import UUID

from app.db.database import get_db
from app.models import Comercio, Producto, Usuario
from app.api.dependencies import get_current_superadmin
from app.schemas.superadmin import ComercioAdminOut, ComercioAdminUpdate

router = APIRouter(prefix="/superadmin", tags=["Super Admin"])

@router.get("/comercios", response_model=List[ComercioAdminOut])
async def list_comercios(
    db: AsyncSession = Depends(get_db),
    admin: Usuario = Depends(get_current_superadmin)
):
    result = await db.execute(select(Comercio).order_by(Comercio.created_at.desc()))
    return result.scalars().all()

@router.put("/comercios/{comercio_id}", response_model=ComercioAdminOut)
async def update_comercio(
    comercio_id: UUID,
    update_data: ComercioAdminUpdate,
    db: AsyncSession = Depends(get_db),
    admin: Usuario = Depends(get_current_superadmin)
):
    result = await db.execute(select(Comercio).filter(Comercio.id == comercio_id))
    comercio = result.scalars().first()
    if not comercio:
        raise HTTPException(status_code=404, detail="Comercio no encontrado")
        
    update_dict = update_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(comercio, key, value)
        
    await db.commit()
    await db.refresh(comercio)
    return comercio

@router.delete("/comercios/{comercio_id}")
async def delete_comercio(
    comercio_id: UUID,
    db: AsyncSession = Depends(get_db),
    admin: Usuario = Depends(get_current_superadmin)
):
    result = await db.execute(select(Comercio).filter(Comercio.id == comercio_id))
    comercio = result.scalars().first()
    if not comercio:
        raise HTTPException(status_code=404, detail="Comercio no encontrado")
        
    await db.delete(comercio)
    await db.commit()
    return {"status": "success", "message": "Comercio eliminado"}
