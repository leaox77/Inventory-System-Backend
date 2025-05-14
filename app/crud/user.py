from sqlalchemy.orm import Session
from passlib.context import CryptContext
import bcrypt  # Import bcrypt for password verification
from ..models.user import User
from ..schemas.user import UserCreate, UserUpdate

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_users(db: Session, skip: int = 0, limit: int = 100):
    """Obtiene lista de usuarios"""
    return db.query(User).offset(skip).limit(limit).all()

def get_user(db: Session, user_id: int):
    """Obtiene un usuario por ID"""
    return db.query(User).filter(User.user_id == user_id).first()

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def create_user(db: Session, user: UserCreate):
    """Crea un nuevo usuario"""
    hashed_password = pwd_context.hash(user.password)
    db_user = User(
        username=user.username,
        password=user.password,
        password_hash=hashed_password,
        full_name=user.full_name,
        role_id=user.role_id,
        is_active=user.is_active if hasattr(user, 'is_active') else True
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: int, user: UserUpdate):
    """Actualiza un usuario existente"""
    db_user = get_user(db, user_id=user_id)
    if db_user:
        update_data = user.model_dump(exclude_unset=True)

        if 'password' in update_data and update_data['password']:
            new_password = update_data['password'] # Guarda el password sin hashear
            db_user.password = new_password # Asigna el password sin hashear al objeto db_user
            db_user.password_hash = pwd_context.hash(update_data.pop('password')) # Hashea y asigna a password_hash

        for key, value in update_data.items():
            if key != 'password': # Evita reasignar el password (ya lo hicimos)
                setattr(db_user, key, value)
        db.commit()
        db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int):
    """Elimina un usuario"""
    db_user = get_user(db, user_id=user_id)
    if db_user:
        db.delete(db_user)
        db.commit()
        return True
    return False

def authenticate_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False
    if user.password != password:  # Aquí comparamos la contraseña en texto plano
        return False
    return user

