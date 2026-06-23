from pydantic import BaseModel, EmailStr
from uuid import UUID

from typing import Optional

class ComercioCreate(BaseModel):
    nombre: str
    whatsapp: str
    descripcion: Optional[str] = None
    tema: Optional[str] = "terracotta"

class UsuarioCreate(BaseModel):
    email: EmailStr
    password: str

class RegistroRequest(BaseModel):
    comercio: ComercioCreate
    usuario: UsuarioCreate

class Token(BaseModel):
    access_token: str
    token_type: str

class UsuarioOut(BaseModel):
    id: UUID
    email: EmailStr
    comercio_id: UUID

    class Config:
        from_attributes = True

class PerfilUpdate(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    whatsapp: str
    email: EmailStr

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    password: str

