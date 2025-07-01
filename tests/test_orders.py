import os

import jwt
from dotenv import load_dotenv
from fastapi.testclient import TestClient

from src.main import app

load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")

client = TestClient(app)


def test_not_found_order():
    response = client.get("/orders/123")
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Order 123 not found",
        "path": "/orders/123",
        "status_code": 404,
    }


def test_create_order_unauthenticated():
    data = {
        "orderId": "123",
        "createdAt": "2021-01-01T00:00:00Z",
        "totalAmount": 100,
        "currency": "USD",
    }
    response = client.post("/orders", json=data)
    assert response.status_code == 403
    assert response.json() == {
        "detail": "Not authenticated",
        "path": "/orders",
        "status_code": 403,
    }


def test_create_order_unauthorized():
    token = jwt.encode(
        {"scopes": "orders:read"}, JWT_SECRET, algorithm=JWT_ALGORITHM
    )
    data = {
        "orderId": "123",
        "createdAt": "2021-01-01T00:00:00Z",
        "totalAmount": 100,
        "currency": "USD",
    }
    response = client.post(
        "/orders", json=data, headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 403
    assert response.json() == {
        "detail": "User does not have permission to write orders",
        "path": "/orders",
        "status_code": 403,
    }


def test_create_order():
    token = jwt.encode(
        {"scopes": "orders:write"}, JWT_SECRET, algorithm=JWT_ALGORITHM
    )
    data = {
        "orderId": "123",
        "createdAt": "2021-01-01T00:00:00Z",
        "totalAmount": 100,
        "currency": "USD",
    }
    response = client.post(
        "/orders", json=data, headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 201
    assert response.json() == data


def test_existing_order():
    token = jwt.encode(
        {"scopes": "orders:write"}, JWT_SECRET, algorithm=JWT_ALGORITHM
    )
    data = {
        "orderId": "123",
        "createdAt": "2021-01-01T00:00:00Z",
        "totalAmount": 100,
        "currency": "USD",
    }
    response = client.post(
        "/orders", json=data, headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 400
    assert response.json() == {
        "detail": "Order already exists",
        "path": "/orders",
        "status_code": 400,
    }


def test_get_order():
    data = {
        "orderId": "123",
        "createdAt": "2021-01-01T00:00:00Z",
        "totalAmount": 100,
        "currency": "USD",
    }
    response = client.get("/orders/123")
    assert response.status_code == 200
    assert response.json() == data
