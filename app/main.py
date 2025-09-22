from contextlib import asynccontextmanager

from mangum import Mangum
from app.core.logger import logger
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os

from app.routers import users


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting API")
    yield
    logger.info("Shutting down API")


app = FastAPI(lifespan=lifespan)

# Routers
app.include_router(users.router)

# Add static files
static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/")
async def root():
    return {"message": "Hello root!"}


handler = Mangum(app, lifespan="off")
