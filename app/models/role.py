from sqlalchemy import Column, String, Integer, JSON
from sqlalchemy.orm import relationship
from .base import Base

class Role(Base):
    __tablename__ = "roles"

    role_id = Column(Integer, primary_key=True, autoincrement=True)  # Agregado
    name = Column(String(50), nullable=False, unique=True)
    permissions = Column(JSON, nullable=False, default={})

    users = relationship("User", back_populates="role")
