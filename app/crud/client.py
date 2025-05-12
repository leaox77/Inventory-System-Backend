from sqlalchemy.orm import Session
from models.client import Client
from schemas.client import ClientCreate
import models

def create_client(db: Session, client: ClientCreate) -> Client:
    db_client = Client(**client.model_dump())
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client

def get_client(db: Session, client_id: int) -> Client | None:
    return db.query(Client).filter(Client.client_id == client_id).first()

def get_clients(db: Session, skip: int = 0, limit: int = 100) -> list[Client]:
    return db.query(Client).offset(skip).limit(limit).all()

def update_client(db: Session, client_id: int, updated_data: ClientCreate) -> Client | None:
    client = db.query(Client).filter(Client.client_id == client_id).first()
    if client:
        for key, value in updated_data.model_dump().items():
            setattr(client, key, value)
        db.commit()
        db.refresh(client)
    return client

def delete_client(db: Session, client_id: int) -> bool:
    client = db.query(Client).filter(Client.client_id == client_id).first()
    if client:
        db.delete(client)
        db.commit()
        return True
    return False

def get_client_by_nit(db: Session, nit: str):
    return db.query(models.Client).filter(models.Client.nit == nit).first()