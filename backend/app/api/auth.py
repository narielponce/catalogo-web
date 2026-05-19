from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import timedelta, datetime, timezone
import re
import uuid

from app.db.database import get_db
from app.models import Comercio, Usuario
from app.schemas.auth import RegistroRequest, Token, UsuarioOut
from app.schemas.public import ComercioPublic
from app.core.security import get_password_hash, verify_password, create_access_token
from app.core.config import settings
from app.api.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["Autenticación"])

def generar_slug(nombre: str) -> str:
    # Convertir a minúsculas y reemplazar espacios por guiones
    slug = nombre.lower().strip()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    return re.sub(r'[\s-]+', '-', slug)

@router.post("/register", response_model=UsuarioOut)
async def register(req: RegistroRequest, db: AsyncSession = Depends(get_db)):
    # Verificar si el email ya existe
    result = await db.execute(select(Usuario).filter(Usuario.email == req.usuario.email))
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="El email ya está registrado")
    
    # Crear el comercio
    slug_base = generar_slug(req.comercio.nombre)
    slug = slug_base
    
    # Verificar si el slug existe
    result_slug = await db.execute(select(Comercio).filter(Comercio.slug == slug))
    if result_slug.scalars().first():
        slug = f"{slug_base}-{req.comercio.whatsapp[-4:]}" # Añadir sufijo si existe
        
    nuevo_comercio = Comercio(
        nombre=req.comercio.nombre,
        slug=slug,
        whatsapp=req.comercio.whatsapp,
        descripcion=req.comercio.descripcion,
        tema=req.comercio.tema or "terracotta",
        activo=True,
        trial_vence=datetime.now(timezone.utc) + timedelta(days=14)
    )
    db.add(nuevo_comercio)
    await db.flush() # Para obtener el ID del comercio generado
    
    # Crear el usuario dueño
    nuevo_usuario = Usuario(
        comercio_id=nuevo_comercio.id,
        email=req.usuario.email,
        hashed_password=get_password_hash(req.usuario.password)
    )
    db.add(nuevo_usuario)
    await db.commit()
    await db.refresh(nuevo_usuario)
    
    return nuevo_usuario

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    # Buscar usuario por email (form_data.username mapea al campo email)
    result = await db.execute(select(Usuario).filter(Usuario.email == form_data.username))
    user = result.scalars().first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    # Generar JWT Token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "comercio_id": str(user.comercio_id)},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me")
async def get_me(db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    response = {
        "id": current_user.id,
        "email": current_user.email,
        "is_superuser": current_user.is_superuser
    }
    
    if current_user.comercio_id:
        result = await db.execute(select(Comercio).filter(Comercio.id == current_user.comercio_id))
        comercio = result.scalars().first()
        if comercio:
            response["comercio"] = {
                "nombre": comercio.nombre,
                "slug": comercio.slug,
                "whatsapp": comercio.whatsapp,
                "descripcion": comercio.descripcion,
                "logo_url": comercio.logo_url,
                "tema": comercio.tema,
                "activo": comercio.activo,
                "trial_vence": comercio.trial_vence.isoformat() if comercio.trial_vence else None
            }
            
    return response

from pydantic import BaseModel
class TemaUpdate(BaseModel):
    tema: str

@router.put("/me/tema")
async def update_tema(
    req: TemaUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    if not current_user.comercio_id:
        raise HTTPException(status_code=400, detail="El usuario no tiene un comercio")
        
    result = await db.execute(select(Comercio).filter(Comercio.id == current_user.comercio_id))
    comercio = result.scalars().first()
    
    if comercio:
        comercio.tema = req.tema
        await db.commit()
        return {"status": "success", "tema": comercio.tema}
    raise HTTPException(status_code=404, detail="Comercio no encontrado")

@router.post("/me/logo")
async def upload_logo(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="El archivo no es una imagen")
        
    file_extension = "webp" if "webp" in file.content_type else file.filename.split(".")[-1]
    file_name = f"logo_{current_user.comercio_id}_{uuid.uuid4().hex[:8]}.{file_extension}"
    file_path = f"/app/uploads/{file_name}"
    
    content = await file.read()
    with open(file_path, 'wb') as out_file:
        out_file.write(content)
        
    logo_url = f"/uploads/{file_name}"
    
    result = await db.execute(select(Comercio).filter(Comercio.id == current_user.comercio_id))
    comercio = result.scalars().first()
    comercio.logo_url = logo_url
    
    await db.commit()
    
    return {"logo_url": logo_url}

@router.post("/me/simular-pago")
async def simular_pago(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    result = await db.execute(select(Comercio).filter(Comercio.id == current_user.comercio_id))
    comercio = result.scalars().first()
    
    if not comercio:
        raise HTTPException(status_code=404, detail="Comercio no encontrado")
        
    comercio.activo = True
    await db.commit()
    
    return {"status": "success", "message": "Pago simulado con éxito. Cuenta activada."}
