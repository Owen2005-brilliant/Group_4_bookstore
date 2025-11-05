import sqlite3
from pymongo import MongoClient
from pathlib import Path

# 配置区 
SQLITE_PATH = Path(r"D:\华师大\大三\当代数据管理系统\大作业1\Bookstore\bookstore\fe\data\book_lx.db")  # 改成你的实际路径
TABLE_NAME = "book"
BATCH_SIZE = 1000
MONGO_URI = "mongodb://localhost:27017"
MONGO_DB = "bookstore"
MONGO_COLLECTION = "books"

def main():
    # 连接 SQLite
    conn = sqlite3.connect(SQLITE_PATH)
    cur = conn.cursor()  

    # 获取总行数
    cur.execute(f"SELECT COUNT(*) FROM {TABLE_NAME}")
    total_rows = cur.fetchone()[0]
    print(f"[INFO] Total rows in `{TABLE_NAME}`: {total_rows}")

    # 连接 MongoDB
    client = MongoClient(MONGO_URI)
    db = client[MONGO_DB]
    col = db[MONGO_COLLECTION]

    offset = 0
    inserted = 0

    # 分批读取 SQLite 并写入 Mongo
    while True:
        cur.execute(f"""
            SELECT id, title, author, publisher, original_title, translator,
                   pub_year, pages, price, currency_unit, binding, isbn,
                   author_intro, book_intro, content, tags
            FROM {TABLE_NAME}
            LIMIT ? OFFSET ?
        """, (BATCH_SIZE, offset))

        rows = cur.fetchall()
        if not rows:
            break

        col_names = [desc[0] for desc in cur.description]
        docs = [dict(zip(col_names, r)) for r in rows]

        if docs:
            col.insert_many(docs)
            inserted += len(docs)
            print(f"[INFO] Inserted {inserted}/{total_rows}")

        offset += BATCH_SIZE

    print("[DONE] Import completed successfully!")
    conn.close()

if __name__ == "__main__":
    main()
