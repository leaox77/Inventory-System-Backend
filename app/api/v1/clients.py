from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.sql import or_
from typing import List, Optional
from app.database import get_db
from app.schemas.client import ClientOut, ClientCreate  # Asegúrate de importar los esquemas
from app.models.client import Client  # El modelo SQLAlchemy solo para consultas

router = APIRouter(prefix="/clients", tags=["clients"])

@router.get("/", response_model=List[ClientOut])  # Cambiado a ClientOut
def read_clients(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Obtiene una lista de clientes.
    """
    clients = db.query(Client).offset(skip).limit(limit).all()
    return clients

@router.get("/search", response_model=List[ClientOut])
def search_clients(
    search_term: str = None,  # Cambiamos a un único parámetro
    db: Session = Depends(get_db)
):
    query = db.query(Client)
    if search_term:
        query = query.filter(
            or_(
                Client.ci_nit.ilike(f"%{search_term}%"),
                Client.full_name.ilike(f"%{search_term}%")
            )
        )
    return query.limit(20).all()

@router.get("/{client_id}", response_model=ClientOut)  # ClientOut aquí
def read_client(
    client_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene un cliente por su ID.
    """
    client = db.query(Client).filter(Client.client_id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return client

@router.post("/", response_model=ClientOut, status_code=201)  # ClientOut aquí
def create_client(
    client: ClientCreate,  # Usamos ClientCreate para la entrada
    db: Session = Depends(get_db)
):
    """
    Crea un nuevo cliente.
    """
    db_client = Client(**client.model_dump())  # Convertimos el schema Pydantic a modelo SQLAlchemy
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client  # FastAPI convertirá automáticamente a ClientOut

@router.put("/{client_id}", response_model=ClientOut)  # ClientOut aquí
def update_client(
    client_id: int,
    client: ClientCreate,  # Usamos ClientCreate para la entrada
    db: Session = Depends(get_db)
):
    """
    Actualiza un cliente existente.
    """
    db_client = db.query(Client).filter(Client.client_id == client_id).first()
    if not db_client:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    for key, value in client.model_dump().items():
        setattr(db_client, key, value)
    
    db.commit()
    db.refresh(db_client)
    return db_client