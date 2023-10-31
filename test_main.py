import pytest
import os
from fastapi.testclient import TestClient
from tinydb import TinyDB
from main import app, Restaurant, Review  # Ajuste conforme o nome do arquivo que você salvou

client = TestClient(app)

# Definindo um nome específico para o banco de dados de teste para evitar conflitos
db_test_path = 'test_db.json'


@pytest.fixture(autouse=True)
def clean_db():
    # Limpando o banco de dados de teste antes e depois de cada teste
    if os.path.exists(db_test_path):
        os.remove(db_test_path)
    db = TinyDB(db_test_path)
    os.remove(db_test_path)


def test_create_restaurant():
    response = client.post(
        "/restaurants/",
        json={"name": "Test Restaurant", "address": "123 Test St", "cuisine": "Test Cuisine"}
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Test Restaurant"


def test_read_restaurant():
    client.post(
        "/restaurants/",
        json={"name": "Test Restaurant", "address": "123 Test St", "cuisine": "Test Cuisine"}
    )
    response = client.get("/restaurants/1")
    assert response.status_code == 200
    assert response.json()["name"] == "Test Restaurant"


def test_read_all_restaurants():
    client.post(
        "/restaurants/",
        json={"name": "Test Restaurant", "address": "123 Test St", "cuisine": "Test Cuisine"}
    )
    response = client.get("/restaurants/")
    assert response.status_code == 200
    assert len(response.json()) > 0


def test_create_review():
    client.post(
        "/restaurants/",
        json={"name": "Test Restaurant", "address": "123 Test St", "cuisine": "Test Cuisine"}
    )
    response = client.post(
        "/restaurants/1/reviews/",
        json={"rating": 5.0, "comment": "Great!"}
    )
    assert response.status_code == 200
    assert response.json()["rating"] == 5.0


def test_read_reviews():
    client.post(
        "/restaurants/",
        json={"name": "Test Restaurant", "address": "123 Test St", "cuisine": "Test Cuisine"}
    )
    client.post(
        "/restaurants/1/reviews/",
        json={"rating": 5.0, "comment": "Great!"}
    )
    response = client.get("/reviews/")
    assert response.status_code == 200
    assert len(response.json()) > 0


def test_read_review():
    client.post(
        "/restaurants/",
        json={"name": "Test Restaurant", "address": "123 Test St", "cuisine": "Test Cuisine"}
    )
    client.post(
        "/restaurants/1/reviews/",
        json={"rating": 5.0, "comment": "Great!"}
    )
    response = client.get("/reviews/", params={"review_id": 1})
    assert response.status_code == 200
    assert response.json()[0]["rating"] == 5.0
