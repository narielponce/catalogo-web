from sqlalchemy import Column, String, Boolean, ForeignKey, Float, DateTime, Index
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
import uuid

Base = declarative_base()

class Comercio(Base):
    __tablename__ = 'comercios'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nombre = Column(String(100), nullable=False)
    slug = Column(String(100), unique=True, index=True, nullable=False) # ej: misitio.com/slug
    descripcion = Column(String(200), nullable=True)
    logo_url = Column(String(500), nullable=True)
    whatsapp = Column(String(20), nullable=False)
    tema = Column(String(50), default="terracotta")
    activo = Column(Boolean, default=True)
    trial_vence = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    usuarios = relationship("Usuario", back_populates="comercio", cascade="all, delete-orphan", passive_deletes=True)
    productos = relationship("Producto", back_populates="comercio", cascade="all, delete-orphan", passive_deletes=True)

class Usuario(Base):
    __tablename__ = 'usuarios'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    comercio_id = Column(UUID(as_uuid=True), ForeignKey('comercios.id', ondelete='CASCADE'), nullable=True)
    email = Column(String(150), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    
    comercio = relationship("Comercio", back_populates="usuarios")
    
    __table_args__ = (
        Index('ix_usuarios_comercio_id', 'comercio_id'),
    )

class Producto(Base):
    __tablename__ = 'productos'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    comercio_id = Column(UUID(as_uuid=True), ForeignKey('comercios.id', ondelete='CASCADE'), nullable=False)
    nombre = Column(String(150), nullable=False)
    descripcion = Column(String(500))
    precio = Column(Float, nullable=False)
    imagen_url = Column(String(255)) # URL de la imagen WebP optimizada
    disponible = Column(Boolean, default=True)
    categoria = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    comercio = relationship("Comercio", back_populates="productos")
    
    # Índice compuesto CLAVE para el catálogo: 
    # Optimiza las búsquedas del cliente final por comercio_id, buscando productos disponibles y ordenando/filtrando por categoría.
    __table_args__ = (
        Index('ix_productos_cat_publico', 'comercio_id', 'disponible', 'categoria'),
    )
