from pymongo import MongoClient

MONGO_URI = "mongodb://localhost:27017"
MONGO_DB_NAME = "bookstore"

# 做成单例，避免每次新建连接
_client = None
_db = None

def get_client():
    global _client
    if _client is None:
        _client = MongoClient(MONGO_URI)
    return _client

def get_db():
    global _db
    if _db is None:
        _db = get_client()[MONGO_DB_NAME]
    return _db

def get_books_collection():
    db = get_db()
    return db["books"]
