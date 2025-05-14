from pydantic import BaseModel
from typing import Optional
from .role import RoleOut  # Asegúrate de tener el modelo RoleOut

# BaseModel para los datos comunes
class UserBase(BaseModel):
    username: str
    password: str | None = None  # Este campo es opcional para la salida
    full_name: str | None = None

# Crear un nuevo usuario
class UserCreate(UserBase):
    password: str  # Este campo es obligatorio para la creación de un nuevo usuario
    role_id: int
    is_active: Optional[bool] = True

# Salida de un usuario
class UserOut(UserBase):
    user_id: int
    is_active: bool
    role: Optional[RoleOut] = None

    class Config:
        from_attributes = True  # Asegura que Pydantic pueda trabajar con atributos de SQLAlchemy

# Actualización de un usuario (campos opcionales)
class UserUpdate(BaseModel):
    username: str | None = None
    full_name: str | None = None
    password: str | None = None  # Este campo también es opcional, ya que podría no querer cambiarlo
    role_id: Optional[int] = None  # Añadido este campo
    is_active: Optional[bool] = None
