from app.database import Base, engine
from app.models import (
    Role, User, Category, Product, 
    Branch, Inventory, Client, Sale, SaleDetail
)
import sys
import os

# Añadir el directorio raíz del proyecto al PATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database import Base, engine
from app.models import *

def init_db():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db()
    print("Base de datos inicializada correctamente")