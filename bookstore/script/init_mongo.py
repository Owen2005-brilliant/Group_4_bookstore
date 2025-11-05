"""
初始化本地 MongoDB，用于bookstore项目
- 创建常用索引
- 可选插入示例店铺/用户
"""

from pymongo import MongoClient
import time

MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "bookstore"

def main():
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]

    # 1) books 索引（全局书库）
    # 唯一id
    db.books.create_index("id", unique=True)
    # 常用查询字段
    db.books.create_index("title")
    db.books.create_index("author")
    # 全文索引（如果Mongo版本支持）
    try:
        db.books.create_index([
            ("title", "text"),
            ("author", "text"),
            ("book_intro", "text"),
            ("tags", "text"),
        ])
    except Exception as e:
        print("text index failed (maybe version not support):", e)

    # 2) stores
    db.stores.create_index("store_id", unique=True)
    db.stores.create_index("user_id")

    # 3) store_books: 某个店里的书
    # 店+书唯一
    db.store_books.create_index(
        [("store_id", 1), ("book_id", 1)],
        unique=True
    )
    # 店内搜索
    db.store_books.create_index("title")

    # 4) users: 放余额的
    db.users.create_index("user_id", unique=True)

    # 5) orders
    db.orders.create_index("order_id", unique=True)
    db.orders.create_index("buyer_id")
    db.orders.create_index("store_id")
    db.orders.create_index("status")
    db.orders.create_index("created_time")

    # 6) order_items
    db.order_items.create_index("order_id")

    # 示例调试
    if not db.users.find_one({"user_id": "demo_user"}):
        db.users.insert_one({"user_id": "demo_user", "balance": 50000})
    if not db.stores.find_one({"store_id": "demo_store"}):
        db.stores.insert_one({"store_id": "demo_store", "user_id": "demo_user", "store_name": "示例书店"})

    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] MongoDB init done.")

if __name__ == "__main__":
    main()
