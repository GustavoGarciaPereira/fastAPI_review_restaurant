import os

from fastapi import FastAPI, HTTPException, status, Query
from pydantic import BaseModel
from tinydb import TinyDB, Query as TinyDBQuery

# Inicialize o FastAPI e o TinyDB
app = FastAPI()
# Obtenha o caminho do banco de dados da variável de ambiente ou use um padrão
db_path = os.environ.get('DB_PATH', 'db.json')
db = TinyDB(db_path)

class Restaurant(BaseModel):
    name: str
    address: str
    cuisine: str

class Review(BaseModel):
    rating: float
    comment: str

@app.post("/restaurants/")
async def create_restaurant(restaurant: Restaurant):
    restaurant_id = len(db.table('restaurants')) + 1
    db.table('restaurants').insert({'id': restaurant_id, **restaurant.model_dump()})
    return {"id": restaurant_id, **restaurant.model_dump()}

@app.get("/restaurants/{restaurant_id}")
async def read_restaurant(restaurant_id: int):
    restaurant = db.table('restaurants').get(doc_id=restaurant_id)
    if restaurant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Restaurant not found")
    return restaurant


@app.get("/restaurants/")
async def read_restaurant():
    restaurant = db.table('restaurants').all()
    if restaurant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Restaurant not found")
    return restaurant


@app.post("/restaurants/{restaurant_id}/reviews/")
async def create_review(restaurant_id: int, review: Review):
    # Verifique se o restaurante existe
    restaurant = db.table('restaurants').get(doc_id=restaurant_id)
    if restaurant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Restaurant not found")
    
    # Crie uma nova avaliação e associe-a ao restaurante
    review_id = len(db.table('reviews')) + 1
    db.table('reviews').insert({'id': review_id, 'restaurant_id': restaurant_id, **review.model_dump()})
    
    return {"message": "Review added successfully", "review_id": review_id, **review.model_dump()}

@app.get("/reviews/")
async def read_reviews(restaurant_id: int = Query(None), review_id: int = Query(None)):
    # Cria uma nova instância de TinyDBQuery para construir consultas
    query = TinyDBQuery()
    
    # Se um review_id é fornecido, retorne a avaliação específica
    if review_id is not None:
        review = db.table('reviews').get(query.id == review_id)
        if review is None:
            raise HTTPException(status_code=404, detail="Review not found")
        return [review]  # Retorne uma lista contendo a avaliação específica
    
    # Se um restaurant_id é fornecido, retorne todas as avaliações para aquele restaurante
    elif restaurant_id is not None:
        reviews = db.table('reviews').search(query.restaurant_id == restaurant_id)
        return reviews
    
    # Se nenhum ID é fornecido, retorne todas as avaliações
    else:
        reviews = db.table('reviews').all()
        return reviews