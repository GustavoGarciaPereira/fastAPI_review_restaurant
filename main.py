import os
from fastapi import FastAPI, HTTPException, status, Query, Request
from pydantic import BaseModel
from tinydb import TinyDB, Query as TinyDBQuery
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="templates")
db_path = os.environ.get('DB_PATH', 'db.json')
db = TinyDB(db_path)


class Restaurant(BaseModel):
    name: str
    address: str
    cuisine: str


class Review(BaseModel):
    rating: float
    comment: str


class RestaurantRepository:
    table = db.table('restaurants')

    @classmethod
    def create(cls, restaurant: Restaurant) -> dict:
        restaurant_id = len(cls.table) + 1
        cls.table.insert({'id': restaurant_id, **restaurant.dict()})
        return {'id': restaurant_id, **restaurant.dict()}

    @classmethod
    def get(cls, restaurant_id: int) -> dict:
        return cls.table.get(doc_id=restaurant_id)

    @classmethod
    def get_all(cls) -> list:
        return cls.table.all()


class ReviewRepository:
    table = db.table('reviews')

    @classmethod
    def create(cls, restaurant_id: int, review: Review) -> dict:
        review_id = len(cls.table) + 1
        cls.table.insert({'id': review_id, 'restaurant_id': restaurant_id, **review.dict()})
        return {'id': review_id, **review.dict()}

    @classmethod
    def get(cls, review_id: int) -> dict:
        query = TinyDBQuery()
        return cls.table.get(query.id == review_id)

    @classmethod
    def get_by_restaurant(cls, restaurant_id: int) -> list:
        query = TinyDBQuery()
        return cls.table.search(query.restaurant_id == restaurant_id)

    @classmethod
    def get_all(cls) -> list:
        return cls.table.all()


@app.post("/restaurants/")
async def create_restaurant(restaurant: Restaurant):
    return RestaurantRepository.create(restaurant)


@app.get("/restaurants/{restaurant_id}")
async def read_restaurant(restaurant_id: int):
    restaurant = RestaurantRepository.get(restaurant_id)
    if restaurant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Restaurant not found")
    return restaurant


@app.get("/restaurants/")
async def read_all_restaurants():
    return RestaurantRepository.get_all()


@app.post("/restaurants/{restaurant_id}/reviews/")
async def create_review(restaurant_id: int, review: Review):
    restaurant = RestaurantRepository.get(restaurant_id)
    if restaurant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Restaurant not found")
    return ReviewRepository.create(restaurant_id, review)


@app.get("/reviews/")
async def read_reviews(
    restaurant_id: int = Query(None),
    review_id: int = Query(None)
):
    if review_id:
        review = ReviewRepository.get(review_id)
        if not review:
            raise HTTPException(status_code=404, detail="Review not found")
        return [review]
    elif restaurant_id:
        return ReviewRepository.get_by_restaurant(restaurant_id)
    else:
        return ReviewRepository.get_all()


@app.get("/dashboard")
async def read_dashboard(request: Request):
    reviews = ReviewRepository.get_all()
    return templates.TemplateResponse("dashboard.html", {"request": request, "reviews": reviews})
