from .auth import Token, TokenData, UserLogin, UserCreate
from .user import UserOut, UserUpdate
from .product import ProductCreate, ProductOut, ProductUpdate
from .category import CategoryCreate, CategoryOut
from .inventory import InventoryUpdate, InventoryOut
from .sale import SaleCreate, SaleOut, SaleDetailCreate
from .role import RoleOut, RoleCreate  # Añadir esta línea

__all__ = [
    "Token", "TokenData", "UserLogin", "UserCreate",
    "UserOut", "UserUpdate",
    "ProductCreate", "ProductOut", "ProductUpdate",
    "CategoryCreate", "CategoryOut",
    "InventoryUpdate", "InventoryOut",
    "SaleCreate", "SaleOut", "SaleDetailCreate",
    "RoleOut", "RoleCreate"  # Añadir esta línea
]