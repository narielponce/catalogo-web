import asyncio
import sys
import os

# Añadir el directorio actual al path para poder importar módulos de la app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.database import get_db, async_session
from app.models import Usuario
from app.core.security import get_password_hash
from sqlalchemy.future import select

async def create_superuser(email: str, password: str):
    async with async_session() as db:
        # Verificar si ya existe
        result = await db.execute(select(Usuario).filter(Usuario.email == email))
        user = result.scalars().first()
        
        if user:
            print(f"El usuario {email} ya existe.")
            if not user.is_superuser:
                user.is_superuser = True
                await db.commit()
                print(f"Usuario {email} actualizado a superadmin.")
            return
            
        nuevo_usuario = Usuario(
            email=email,
            hashed_password=get_password_hash(password),
            is_superuser=True,
            comercio_id=None
        )
        db.add(nuevo_usuario)
        await db.commit()
        print(f"Superadmin {email} creado exitosamente.")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python create_superuser.py <email> <password>")
        sys.exit(1)
        
    email = sys.argv[1]
    password = sys.argv[2]
    
    asyncio.run(create_superuser(email, password))
