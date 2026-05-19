from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime, timedelta, timezone
from app.db.database import get_db
from app.models import Comercio, Usuario

router = APIRouter(prefix="/internal/comercios", tags=["n8n-internal"])

N8N_SECRET = "tu_clave_secreta_super_segura_aqui"

def verify_n8n_token(x_n8n_secret_key: str = Header(...)):
    if x_n8n_secret_key != N8N_SECRET:
        raise HTTPException(status_code=403, detail="Forbidden")

@router.get("/vencidos", dependencies=[Depends(verify_n8n_token)])
async def obtener_comercios_vencidos(db: AsyncSession = Depends(get_db)):
    """Devuelve los comercios activos cuyo trial_vence ya expiró, junto al email del dueño para notificarle."""
    now = datetime.now(timezone.utc)
    
    # Hacemos un JOIN para traer el email del usuario dueño
    query = select(Comercio, Usuario.email).join(Usuario, Usuario.comercio_id == Comercio.id).filter(
        Comercio.activo == True,
        Comercio.trial_vence <= now
    )
    result = await db.execute(query)
    vencidos = result.all()
    
    return [
        {
            "id": str(comercio.id),
            "nombre": comercio.nombre,
            "email": email,
            "vencimiento": comercio.trial_vence
        }
        for comercio, email in vencidos
    ]

@router.put("/{comercio_id}/desactivar", dependencies=[Depends(verify_n8n_token)])
async def desactivar_comercio(comercio_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Comercio).filter(Comercio.id == comercio_id))
    comercio = result.scalars().first()
    if not comercio:
        raise HTTPException(status_code=404)
    
    comercio.activo = False
    await db.commit()
    return {"status": "success", "message": "Comercio desactivado"}

@router.put("/{comercio_id}/reactivar", dependencies=[Depends(verify_n8n_token)])
async def reactivar_comercio(comercio_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Comercio).filter(Comercio.id == comercio_id))
    comercio = result.scalars().first()
    if not comercio:
        raise HTTPException(status_code=404)
    
    comercio.activo = True
    
    now = datetime.now(timezone.utc)
    # Si el comercio ya tenía días a favor (el vencimiento es en el futuro), sumamos 30 días a esa fecha.
    # Si estaba vencido, sumamos 30 días a partir de HOY.
    if comercio.trial_vence and comercio.trial_vence > now:
        comercio.trial_vence = comercio.trial_vence + timedelta(days=30)
    else:
        comercio.trial_vence = now + timedelta(days=30)
        
    await db.commit()
    return {"status": "success", "message": "Suscripción renovada por 30 días adicionales"}
