import logging
from pymongo import MongoClient
from typing import Any
from pymongo.collection import Collection
from app.core.config import settings

MONGODB_URL = settings.MONGODB_URL
try:
    client: MongoClient[dict[str, Any]] = MongoClient(
        MONGODB_URL,
    )
    db = client.get_database(settings.MONGODB_DB_NAME)
    users_collection: Collection[dict[str, Any]] = db.get_collection("users")

    # Test the connection
    client.admin.command('ping')
    logging.info("Connected to MongoDB")
except Exception as e:
    logging.critical(f"Failed to connect to MongoDB: {str(e)}")
    raise
