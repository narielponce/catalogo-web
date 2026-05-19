from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from uuid import UUID
import uuid
import os

from app.db.database import get_db
from app.models import Producto, Usuario
from app.schemas.productos import ProductoCreate, ProductoUpdate, ProductoOut
from app.api.dependencies import get_current_user

router = APIRouter(prefix="/productos", tags=["Productos Privados"])

@router.get("/", response_model=List[ProductoOut])
async def list_productos(
    db: AsyncSession = Depends(get_db), 
    current_user: Usuario = Depends(get_current_user)
):
    """Lista todos los productos del comercio del usuario logueado"""
    result = await db.execute(
        select(Producto).filter(Producto.comercio_id == current_user.comercio_id)
    )
    return result.scalars().all()

@router.post("/upload-image")
async def upload_image(
    file: UploadFile = File(...),
    current_user: Usuario = Depends(get_current_user)
):
    """Sube una imagen comprimida a WebP y devuelve la URL"""
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="El archivo no es una imagen")
        
    # Generar un nombre único para evitar colisiones
    file_extension = "webp" if "webp" in file.content_type else file.filename.split(".")[-1]
    file_name = f"{uuid.uuid4().hex}.{file_extension}"
    file_path = f"/app/uploads/{file_name}"
    
    # Guardar en disco
    content = await file.read()
    with open(file_path, 'wb') as out_file:
        out_file.write(content)
        
    return {"url": f"/uploads/{file_name}"}

@router.post("/", response_model=ProductoOut)
async def create_producto(
    producto_in: ProductoCreate, 
    db: AsyncSession = Depends(get_db), 
    current_user: Usuario = Depends(get_current_user)
):
    """Crea un nuevo producto asegurando el aislamiento por comercio_id"""
    nuevo_producto = Producto(
        **producto_in.model_dump(),
        comercio_id=current_user.comercio_id
    )
    db.add(nuevo_producto)
    await db.commit()
    await db.refresh(nuevo_producto)
    return nuevo_producto

@router.put("/{producto_id}", response_model=ProductoOut)
async def update_producto(
    producto_id: UUID,
    producto_in: ProductoUpdate, 
    db: AsyncSession = Depends(get_db), 
    current_user: Usuario = Depends(get_current_user)
):
    """Actualiza un producto asegurando que pertenezca al usuario"""
    result = await db.execute(
        select(Producto).filter(Producto.id == producto_id, Producto.comercio_id == current_user.comercio_id)
    )
    producto = result.scalars().first()
    
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
        
    update_data = producto_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(producto, key, value)
        
    await db.commit()
    await db.refresh(producto)
    return producto

@router.delete("/{producto_id}")
async def delete_producto(
    producto_id: UUID,
    db: AsyncSession = Depends(get_db), 
    current_user: Usuario = Depends(get_current_user)
):
    result = await db.execute(
        select(Producto).filter(Producto.id == producto_id, Producto.comercio_id == current_user.comercio_id)
    )
    producto = result.scalars().first()
    
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
        
    await db.delete(producto)
    await db.commit()
    return {"detail": "Producto eliminado exitosamente"}
