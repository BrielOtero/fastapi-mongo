import logging
from pymongo import MongoClient
from typing import Any
from pymongo.collection import Collection
from app.core.config import settings
from app.models.users import UserDB


try:
    client: MongoClient[dict[str, Any]] = MongoClient(
        settings.MONGODB_URL,
        connectTimeoutMS=5000,  # 5 second connection timeout
        serverSelectionTimeoutMS=5000,  # 5 second server selection timeout
        maxPoolSize=10,
        minPoolSize=0,
    )
    db = client.get_database(settings.MONGODB_DB_NAME)
    users_collection: Collection[dict[str, UserDB]] = db.get_collection("users")
    logging.info("Connected to MongoDB")
except Exception as e:
    logging.critical(f"Failed to connect to MongoDB: {str(e)}", exc_info=True)
