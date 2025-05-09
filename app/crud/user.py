from sqlalchemy.orm import Session
from passlib.context import CryptContext
import bcrypt  # Import bcrypt for password verification
from ..models.user import User
from ..schemas.user import UserCreate

# Inicialización del contexto para manejar bcrypt con passlib
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_user(db: Session, user_id: int):
    """Recupera un usuario de la base de datos por su ID."""
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    """Recupera un usuario de la base de datos por su correo electrónico."""
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, user: UserCreate):
    """Crea un nuevo usuario, asegurándose de que la contraseña esté correctamente hasheada."""
    # Hashear la contraseña antes de almacenarla
    hashed_password = pwd_context.hash(user.password)
    
    # Crear un nuevo objeto User con los datos proporcionados
    db_user = User(
        username=user.username,
        password_hash=hashed_password,  # Usamos el campo correcto para almacenar el hash
        full_name=user.full_name
    )
    
    # Agregar el nuevo usuario a la base de datos
    db.add(db_user)
    db.commit()
    db.refresh(db_user)  # Actualizar el objeto para tener los datos más recientes
    return db_user

def authenticate_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False
    if user.password != password:  # Aquí comparamos la contraseña en texto plano
        return False
    return user

