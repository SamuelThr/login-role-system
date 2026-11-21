from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class RolBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None

class RolResponse(RolBase):
    id: int

    class Config:
        from_attributes = True

class UsuarioCreate(BaseModel):
    username: str = Field(...,min_length=3,max_length=50)
    email: str = Field(...,min_length=5, max_length=100)
    password: str = Field(...,min_length=6)
    rol_nombre: str = "USER"

class UsuarioResponse(BaseModel):
    id: int
    username: str
    email: str
    activo: bool
    fecha_creacion:datetime
    rol: RolResponse

class Token(BaseModel):
    access_token: str
    token_type: str