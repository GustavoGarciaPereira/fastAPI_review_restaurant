import pytest

from fastapi import FastAPI
from fastapi.testclient import TestClient
from tinydb import TinyDB, Query as TinyDBQuery
from main import app, Restaurant, Review  # ajuste o import de acordo com o nome do arquivo que você salvou

client = TestClient(app)


@pytest.fixture(autouse=True)
def clean_db():
    # Substitua isso pela lógica de limpeza do seu banco de dados
    # db.truncate()
    import os
    db_path = os.environ.get('DB_PATH', 'test_db.json')
    db = TinyDB(db_path)
    os.remove(db_path)
    db.truncate()

def test_create_restaurant():
    # ... o restante do seu código de teste ...
    pass


def test_create_restaurant():
    response = client.post(
        "/restaurants/",
        json={"name": "Test Restaurant", "address": "123 Test St", "cuisine": "Test Cuisine"}
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Test Restaurant"

def test_read_restaurant():
    response = client.get("/restaurants/1")
    assert response.status_code == 200
    assert response.json()["name"] == "Test Restaurant"

def test_read_all_restaurants():
    response = client.get("/restaurants/")
    assert response.status_code == 200
    assert len(response.json()) > 0

def test_create_review():
    response = client.post(
        "/restaurants/1/reviews/",
        json={"rating": 5.0, "comment": "Great!"}
    )
    assert response.status_code == 200
    assert response.json()["rating"] == 5.0

def test_read_reviews():
    response = client.get("/reviews/")
    assert response.status_code == 200
    assert len(response.json()) > 0

def test_read_review():
    response = client.get("/reviews/", params={"review_id": 1})
    assert response.status_code == 200
    assert response.json()[0]["rating"] == 5.0
