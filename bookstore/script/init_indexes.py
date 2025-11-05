"""
初始化 MongoDB 索引
创建所有必要的索引以优化查询性能
"""
from pymongo import MongoClient
import time

MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "bookstore"

def main():
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]

    print("开始创建索引...")

    # 1) books 索引（全局书库）
    print("创建 books 集合索引...")
    try:
        db.books.create_index("id", unique=True)
        print("  ✅ id 唯一索引")
    except Exception as e:
        print(f"  ⚠️  id 索引: {e}")
    
    try:
        db.books.create_index("title")
        print("  ✅ title 索引")
    except Exception as e:
        print(f"  ⚠️  title 索引: {e}")
    
    try:
        db.books.create_index("author")
        print("  ✅ author 索引")
    except Exception as e:
        print(f"  ⚠️  author 索引: {e}")
    
    # 全文索引（如果MongoDB版本支持）
    try:
        db.books.create_index([
            ("title", "text"),
            ("author", "text"),
            ("book_intro", "text"),
            ("tags", "text"),
        ])
        print("  ✅ 全文索引")
    except Exception as e:
        print(f"  ⚠️  全文索引不支持: {e}")

    # 2) stores 索引
    print("\n创建 stores 集合索引...")
    try:
        db.stores.create_index("store_id", unique=True)
        print("  ✅ store_id 唯一索引")
    except Exception as e:
        print(f"  ⚠️  store_id 索引: {e}")
    
    try:
        db.stores.create_index("user_id")
        print("  ✅ user_id 索引")
    except Exception as e:
        print(f"  ⚠️  user_id 索引: {e}")

    # 3) store_books 索引
    print("\n创建 store_books 集合索引...")
    try:
        db.store_books.create_index(
            [("store_id", 1), ("book_id", 1)],
            unique=True
        )
        print("  ✅ (store_id, book_id) 复合唯一索引")
    except Exception as e:
        print(f"  ⚠️  复合索引: {e}")
    
    try:
        db.store_books.create_index("title")
        print("  ✅ title 索引")
    except Exception as e:
        print(f"  ⚠️  title 索引: {e}")

    # 4) users 索引
    print("\n创建 users 集合索引...")
    try:
        db.users.create_index("user_id", unique=True)
        print("  ✅ user_id 唯一索引")
    except Exception as e:
        print(f"  ⚠️  user_id 索引: {e}")

    # 5) orders 索引
    print("\n创建 orders 集合索引...")
    try:
        db.orders.create_index("order_id", unique=True)
        print("  ✅ order_id 唯一索引")
    except Exception as e:
        print(f"  ⚠️  order_id 索引: {e}")
    
    try:
        db.orders.create_index("buyer_id")
        print("  ✅ buyer_id 索引")
    except Exception as e:
        print(f"  ⚠️  buyer_id 索引: {e}")
    
    try:
        db.orders.create_index("store_id")
        print("  ✅ store_id 索引")
    except Exception as e:
        print(f"  ⚠️  store_id 索引: {e}")
    
    try:
        db.orders.create_index("status")
        print("  ✅ status 索引")
    except Exception as e:
        print(f"  ⚠️  status 索引: {e}")
    
    try:
        db.orders.create_index("created_time")
        print("  ✅ created_time 索引")
    except Exception as e:
        print(f"  ⚠️  created_time 索引: {e}")

    # 6) order_items 索引
    print("\n创建 order_items 集合索引...")
    try:
        db.order_items.create_index("order_id")
        print("  ✅ order_id 索引")
    except Exception as e:
        print(f"  ⚠️  order_id 索引: {e}")

    print(f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] 索引创建完成！")

if __name__ == "__main__":
    main()
