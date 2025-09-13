from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os

from app.routers import basic_auth_users, products, users

app = FastAPI()

# Routers
app.include_router(users.router)
app.include_router(basic_auth_users.router)
app.include_router(products.router)

# Add static files
static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/")
async def root():
    return {"message": "Hello root!"}
