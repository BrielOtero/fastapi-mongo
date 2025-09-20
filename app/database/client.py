from pymongo import MongoClient
from typing import Any
from pymongo.collection import Collection
from app.core.logger import logger
from app.core.config import settings

import os

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
try:
    client: MongoClient[dict[str, Any]] = MongoClient(MONGODB_URL)
    db = client.get_database(settings.MONGODB_DB_NAME)
    users_collection: Collection[dict[str, Any]] = db.get_collection("users")

    logger.info("Connected to MongoDB")
except Exception as e:
    logger.critical(f"Failed to connect to MongoDB: {str(e)}")
    raise
