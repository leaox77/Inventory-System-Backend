# routers/client.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from app.schemas.client import ClientOut, ClientCreate
from app.crud.client import search_clients as search, get_clients as gets, get_client as get, create_client as create, update_client as update, delete_client as delete
from app.dependencies import get_db
from app.models.user import User
from app.dependencies import get_current_active_user

router = APIRouter(prefix="/clients", tags=["clients"])

@router.get("/", response_model=List[ClientOut])
def read_clients(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtiene lista de clientes con opción de búsqueda"""
    if search:
        return search_clients(db, search_term=search, limit=limit)
    return gets(db, skip=skip, limit=limit)

@router.get("/search", response_model=List[ClientOut])
def search_clients(
    search_term: str,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Búsqueda de clientes por CI/NIT o nombre"""
    return search(db, search_term=search_term, limit=limit)

@router.get("/{client_id}", response_model=ClientOut)
def read_client(
    client_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtiene un cliente por ID"""
    client = get(db, client_id=client_id)
    if client is None:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return client

@router.post("/", response_model=ClientOut, status_code=status.HTTP_201_CREATED)
def create_client(
    client: ClientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Crea un nuevo cliente"""
    return create(db=db, client=client)

@router.put("/{client_id}", response_model=ClientOut)
def update_client(
    client_id: int,
    client: ClientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Actualiza un cliente existente"""
    db_client = get(db, client_id=client_id)
    if db_client is None:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    # Asegúrate de pasar los parámetros en el orden correcto
    return update(db=db, client_id=client_id, updated_data=client)

@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_client(
    client_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Elimina un cliente"""
    if not delete(db, client_id=client_id):
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return {"ok": True}