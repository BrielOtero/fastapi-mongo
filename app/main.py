from contextlib import asynccontextmanager
import logging

from mangum import Mangum
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os

from app.routers import users

logging.getLogger("mangum.lifespan").setLevel(logging.INFO)
logging.getLogger("mangum.http").setLevel(logging.INFO)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.info("Starting API")
    yield
    logging.info("Shutting down API")


app = FastAPI(lifespan=lifespan, redirect_slashes=False)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition", "Content-Type", "Content-Length"],
)

# Routers
app.include_router(users.router)

# Add static files
static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/")
async def root():
    return {"message": "Hello root!"}


handler = Mangum(app, lifespan="auto")
