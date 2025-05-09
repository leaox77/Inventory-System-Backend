from sqlalchemy.orm import Session
from fastapi import HTTPException, status, Depends
from app.database import get_db
from app.utils.security import get_current_active_user
from app.models.user import User

# Dependencia para la base de datos
def get_db_session():
    return get_db

# Dependencia para autenticación
def get_current_user_dependency():
    return get_current_active_user

# Dependencia para administradores
def admin_required(current_user: User = Depends(get_current_active_user)):
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren privilegios de administrador"
        )
    return current_user