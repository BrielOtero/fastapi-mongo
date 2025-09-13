from fastapi import APIRouter, HTTPException, status

from app.models.product import Product

router = APIRouter(prefix="/products", tags=["products"])

products_list = [Product(id=1, name="Tomato")]


# GET /products
@router.get("/")
async def read_products() -> list[Product]:
    return products_list


# GET /products/id
@router.get("/{id}")
async def read_product(id: int) -> Product:
    product = next((p for p in products_list if p.id == id), None)

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )

    return product
