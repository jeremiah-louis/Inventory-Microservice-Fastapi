from typing import Any
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from redis_om import get_redis_connection, HashModel

app = FastAPI()
redis_connection = get_redis_connection(
    host="localhost",
    port=6379,
    decode_responses=True,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_headers=["*"],
    allow_methods=["*"],
)


class CreateProductItem(BaseModel):
    name: str
    price: float
    quantity_available: int


# Instantiate our db_model
class Product(HashModel):
    name: str
    price: float
    quantity_available: int

    # connects the redis_db to the model
    class Meta:
        database = redis_connection


@app.get("/all-items")
def inventory() -> list[dict[str, Any]]:
    return [order_product_by_primary_key(pk) for pk in Product.all_pks()]


def order_product_by_primary_key(pk: str) -> dict[str, Product]:
    # I want to display all the values of the data stored in one primary key
    product = Product.get(pk)
    return {
        "id": product.pk,
        "name": product.name,
        "price": product.price,
        "quantity_available": product.quantity_available,
    }


@app.post("/all-items")
def create_item(product_create: CreateProductItem):
    product = Product(
        name=product_create.name,
        price=product_create.price,
        quantity_available=product_create.quantity_available,
    )
    product.save()
    return product


@app.get("/all-items/{primary_key}")
def get_product_by_id(primary_key: str):
    return Product.get(primary_key)


@app.delete("/all-items/{primary_key}")
def delete_product_by_id(primary_key: str):
    return Product.delete(pk=primary_key)
