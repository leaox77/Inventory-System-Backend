from fastapi import status
from app.schemas.product import ProductCreate

def test_create_product(client, db):
    product_data = {
        "barcode": "7771234567890",
        "name": "Arroz Diana 5kg",
        "description": "Arroz extra blanco",
        "category_id": 1,
        "unit_type": "paquete",
        "price": 25.50,
        "cost": 20.00,
        "min_stock": 10
    }
    response = client.post("/api/v1/products/", json=product_data)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == product_data["name"]
    assert "id" in data