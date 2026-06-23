from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, BackgroundTasks, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import timedelta, datetime, timezone
import re
import uuid
import mercadopago
import urllib.request
import json
import jwt

from app.db.database import get_db
from app.models import Comercio, Usuario
from app.schemas.auth import RegistroRequest, Token, UsuarioOut, PerfilUpdate, ForgotPasswordRequest, ResetPasswordRequest
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
                "portada_url": comercio.portada_url,
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

@router.post("/me/portada")
async def upload_portada(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="El archivo no es una imagen")
        
    file_extension = "webp" if "webp" in file.content_type else file.filename.split(".")[-1]
    file_name = f"portada_{current_user.comercio_id}_{uuid.uuid4().hex[:8]}.{file_extension}"
    file_path = f"/app/uploads/{file_name}"
    
    content = await file.read()
    with open(file_path, 'wb') as out_file:
        out_file.write(content)
        
    portada_url = f"/uploads/{file_name}"
    
    result = await db.execute(select(Comercio).filter(Comercio.id == current_user.comercio_id))
    comercio = result.scalars().first()
    comercio.portada_url = portada_url
    
    await db.commit()
    
    return {"portada_url": portada_url}

@router.post("/me/crear-preferencia")
async def crear_preferencia(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    sdk = mercadopago.SDK(settings.MP_ACCESS_TOKEN)

    preference_data = {
        "items": [
            {
                "title": "Suscripción Mensual - TuPedido.ar",
                "quantity": 1,
                "unit_price": 1000.00,
            }
        ],
        "payer": {
            "email": current_user.email
        },
        "back_urls": {
            "success": "https://tupedido.ar/admin?pago=exito",
            "failure": "https://tupedido.ar/admin?pago=error",
            "pending": "https://tupedido.ar/admin?pago=pendiente"
        },
        "auto_return": "approved",
        "external_reference": str(current_user.comercio_id),
        # Reemplazar url con la IP o dominio real de n8n
        "notification_url": "https://n8n.raizdigital.com.ar/webhook/mercadopago-tupedido"
    }

    try:
        preference_response = sdk.preference().create(preference_data)
        status_code = preference_response.get("status", 500)
        response_body = preference_response.get("response", {})
        
        if status_code >= 400 or "init_point" not in response_body:
            print(f"Error al crear preferencia en MercadoPago (Status {status_code}): {response_body}")
            error_message = response_body.get("message", "Error desconocido de MercadoPago")
            raise HTTPException(
                status_code=400,
                detail=f"MercadoPago: {error_message}"
            )
            
        return {"init_point": response_body["init_point"]}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Excepcion al crear preferencia de MercadoPago: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/me/perfil")
async def update_perfil(
    req: PerfilUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    if not current_user.comercio_id:
        raise HTTPException(status_code=400, detail="El usuario no tiene un comercio")
        
    result = await db.execute(select(Comercio).filter(Comercio.id == current_user.comercio_id))
    comercio = result.scalars().first()
    
    if not comercio:
        raise HTTPException(status_code=404, detail="Comercio no encontrado")
        
    # Verificar si el email ya existe en otro usuario
    if req.email != current_user.email:
        result_email = await db.execute(select(Usuario).filter(Usuario.email == req.email, Usuario.id != current_user.id))
        if result_email.scalars().first():
            raise HTTPException(status_code=400, detail="El email ya está registrado por otro usuario")
        current_user.email = req.email
        
    # Si cambia el nombre, regeneramos el slug (puede cambiar la URL)
    if req.nombre != comercio.nombre:
        slug_base = generar_slug(req.nombre)
        slug = slug_base
        result_slug = await db.execute(select(Comercio).filter(Comercio.slug == slug, Comercio.id != comercio.id))
        if result_slug.scalars().first():
            slug = f"{slug_base}-{req.whatsapp[-4:]}"
        comercio.slug = slug

    comercio.nombre = req.nombre
    comercio.descripcion = req.descripcion
    comercio.whatsapp = req.whatsapp
    
    await db.commit()
    
    return {
        "status": "success",
        "email": current_user.email,
        "comercio": {
            "nombre": comercio.nombre,
            "slug": comercio.slug,
            "whatsapp": comercio.whatsapp,
            "descripcion": comercio.descripcion
        }
    }

def notificar_recuperacion_n8n(email: str, reset_link: str, comercio_nombre: str):
    url = settings.N8N_RECOVER_PASSWORD_WEBHOOK
    data = {
        "email": email,
        "reset_link": reset_link,
        "comercio_nombre": comercio_nombre
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "X-N8N-Secret-Key": settings.N8N_SECRET
        },
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            status_code = response.getcode()
            print(f"[INFO] Webhook de n8n invocado exitosamente. Status: {status_code}")
    except Exception as e:
        print(f"[ERROR] Error al invocar el webhook de n8n: {e}")

@router.post("/forgot-password")
async def forgot_password(
    req: ForgotPasswordRequest,
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Usuario).filter(Usuario.email == req.email))
    user = result.scalars().first()
    
    # Respuesta genérica por seguridad si no existe el usuario
    if not user:
        return {"message": "Si el correo está registrado, recibirás un enlace para restablecer tu contraseña."}
        
    # Generar token JWT con expiración de 15 minutos
    expire = datetime.utcnow() + timedelta(minutes=15)
    token_data = {
        "sub": str(user.id),
        "action": "reset_password",
        "exp": expire
    }
    reset_token = jwt.encode(token_data, settings.JWT_SECRET, algorithm=settings.ALGORITHM)
    
    # Obtener el origen dinámicamente
    from urllib.parse import urlparse
    origin = request.headers.get("origin")
    if not origin:
        referer = request.headers.get("referer")
        if referer:
            parsed = urlparse(referer)
            origin = f"{parsed.scheme}://{parsed.netloc}"
        else:
            origin = "https://tupedido.ar"
    else:
        parsed = urlparse(origin)
        origin = f"{parsed.scheme}://{parsed.netloc}"
        
    reset_link = f"{origin}/reset-password?token={reset_token}"
    
    # Obtener nombre del comercio para el email
    result_comercio = await db.execute(select(Comercio).filter(Comercio.id == user.comercio_id))
    comercio = result_comercio.scalars().first()
    comercio_nombre = comercio.nombre if comercio else "TuPedido.ar"
    
    # Enviar email via n8n en segundo plano
    background_tasks.add_task(
        notificar_recuperacion_n8n,
        email=user.email,
        reset_link=reset_link,
        comercio_nombre=comercio_nombre
    )
    
    response_data = {
        "message": "Si el correo está registrado, recibirás un enlace para restablecer tu contraseña."
    }
    
    if settings.DEBUG:
        response_data["debug_link"] = reset_link
        
    return response_data

@router.post("/reset-password")
async def reset_password(req: ResetPasswordRequest, db: AsyncSession = Depends(get_db)):
    try:
        payload = jwt.decode(req.token, settings.JWT_SECRET, algorithms=[settings.ALGORITHM])
        user_id = payload.get("sub")
        action = payload.get("action")
        
        if not user_id or action != "reset_password":
            raise HTTPException(status_code=400, detail="Token inválido o malformado")
            
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=400, detail="El token ha expirado")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=400, detail="Token inválido o malformado")
        
    result = await db.execute(select(Usuario).filter(Usuario.id == uuid.UUID(user_id)))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
    user.hashed_password = get_password_hash(req.password)
    await db.commit()
    
    return {"message": "Contraseña restablecida exitosamente"}
