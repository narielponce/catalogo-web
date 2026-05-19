from pydantic import BaseModel
from typing import Optional
from uuid import UUID

class ProductoBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    precio: float
    categoria: Optional[str] = None
    imagen_url: Optional[str] = None
    disponible: bool = True

class ProductoCreate(ProductoBase):
    pass

class ProductoUpdate(ProductoBase):
    nombre: Optional[str] = None
    precio: Optional[float] = None

class ProductoOut(ProductoBase):
    id: UUID
    comercio_id: UUID

    class Config:
        from_attributes = True
