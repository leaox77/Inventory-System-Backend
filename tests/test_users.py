from fastapi import status
from app.schemas.user import UserCreate

def test_create_user(client):
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "TestPass123",
        "full_name": "Test User"
    }
    response = client.post("/api/v1/users/", json=user_data)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["email"] == user_data["email"]
    assert "id" in data

def test_login_user(client, test_user):
    login_data = {
        "username": test_user["username"],
        "password": test_user["password"]
    }
    response = client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()