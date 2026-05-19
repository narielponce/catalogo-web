from pydantic import BaseModel
from typing import Optional
from uuid import UUID

class ComercioAdminOut(BaseModel):
    id: UUID
    nombre: str
    slug: str
    whatsapp: str
    descripcion: Optional[str] = None
    logo_url: Optional[str] = None
    activo: bool

    class Config:
        from_attributes = True

class ComercioAdminUpdate(BaseModel):
    nombre: Optional[str] = None
    slug: Optional[str] = None
    activo: Optional[bool] = None
