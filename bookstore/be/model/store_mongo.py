from be.model.mongo_conn import get_db, get_books_collection

class StoreMongo:
    def __init__(self):
        self.db = get_db()
        self.col_stores = self.db["stores"]
        self.col_store_books = self.db["store_books"]
        self.col_books = get_books_collection()

    # 创建店铺
    def create_store(self, store_id: str, user_id: str, store_name: str = ""):
        exist = self.col_stores.find_one({"store_id": store_id})
        if exist:
            return False, "store already exists"
        self.col_stores.insert_one({
            "store_id": store_id,
            "user_id": user_id,
            "store_name": store_name,
        })
        return True, "ok"

    # 添加书籍（从全局书库引用）
    def add_book_to_store(self, store_id: str, book_id: str, price: int = 0, stock_level: int = 0):
        store = self.col_stores.find_one({"store_id": store_id})
        if not store:
            return False, "store not found"

        book = self.col_books.find_one({"id": book_id})
        if not book:
            return False, "book not found in global books"

        existed = self.col_store_books.find_one({"store_id": store_id, "book_id": book_id})
        if existed:
            return False, "book already exists in store"

        self.col_store_books.insert_one({
            "store_id": store_id,
            "book_id": book_id,
            "price": price,
            "stock_level": stock_level,
            "title": book.get("title", ""),
            "author": book.get("author", ""),
        })
        return True, "ok"

    # 增加库存
    def add_stock_level(self, store_id: str, book_id: str, add_amount: int):
        record = self.col_store_books.find_one({"store_id": store_id, "book_id": book_id})
        if not record:
            return False, "book not found in store"

        new_stock = record.get("stock_level", 0) + add_amount
        self.col_store_books.update_one(
            {"store_id": store_id, "book_id": book_id},
            {"$set": {"stock_level": new_stock}}
        )
        return True, "ok"
    
    def add_book_to_store_with_info(self, store_id: str, book_info: dict,
                                    price: int = 0, stock_level: int = 0):
        # 1. 店铺存在不
        store = self.col_stores.find_one({"store_id": store_id})
        if not store:
            return False, "store not found"

        book_id = book_info["id"]

        # 2. 先把这本书写进全局 books
        exist_global = self.col_books.find_one({"id": book_id})
        if not exist_global:
            # 只存规范里有的字段
            doc = {
                "id": book_info.get("id"),
                "title": book_info.get("title", ""),
                "author": book_info.get("author", ""),
                "publisher": book_info.get("publisher", ""),
                "original_title": book_info.get("original_title", ""),
                "translator": book_info.get("translator", ""),
                "pub_year": book_info.get("pub_year", ""),
                "pages": book_info.get("pages"),
                "price": book_info.get("price"),
                "binding": book_info.get("binding", ""),
                "isbn": book_info.get("isbn", ""),
                "author_intro": book_info.get("author_intro", ""),
                "book_intro": book_info.get("book_intro", ""),
                "content": book_info.get("content", ""),
                "tags": book_info.get("tags", []),
                "pictures": book_info.get("pictures", []),
            }
            self.col_books.insert_one(doc)

        # 3. 再往某个店里挂这本书
        existed = self.col_store_books.find_one({"store_id": store_id, "book_id": book_id})
        if existed:
            return False, "book already exists in store"

        self.col_store_books.insert_one({
            "store_id": store_id,
            "book_id": book_id,
            "price": price or book_info.get("price", 0),
            "stock_level": stock_level,
            "title": book_info.get("title", ""),
        })
        return True, "ok"
