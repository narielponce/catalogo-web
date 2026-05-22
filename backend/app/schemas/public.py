from pydantic import BaseModel
from typing import Optional
from uuid import UUID

class ComercioPublic(BaseModel):
    nombre: str
    slug: str
    whatsapp: str
    descripcion: Optional[str] = None
    logo_url: Optional[str] = None
    portada_url: Optional[str] = None
    tema: str

    class Config:
        from_attributes = True

class ProductoPublic(BaseModel):
    id: UUID
    nombre: str
    descripcion: Optional[str] = None
    precio: float
    categoria: Optional[str] = None
    imagen_url: Optional[str] = None

    class Config:
        from_attributes = True
