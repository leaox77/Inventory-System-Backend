from fastapi import status
from app.schemas.sale import SaleCreate, SaleDetailCreate

def test_create_sale(client, auth_token):
    sale_data = {
        "branch_id": 1,
        "payment_method": "EFECTIVO",
        "items": [
            {
                "product_id": 1,
                "quantity": 2,
                "unit_price": 25.50
            }
        ]
    }
    response = client.post(
        "/api/v1/sales/",
        json=sale_data,
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["total"] == 51.00
    assert len(data["details"]) == 1