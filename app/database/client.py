from pymongo import MongoClient
from typing import Any
from pymongo.collection import Collection

import os

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")

client: MongoClient[dict[str, Any]] = MongoClient(MONGODB_URL)
db = client.get_database("local")
users_collection: Collection[dict[str, Any]] = db.get_collection("users")
