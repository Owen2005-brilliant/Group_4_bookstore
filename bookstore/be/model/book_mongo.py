from be.model.mongo_conn import get_books_collection

class BookMongo:
    def __init__(self):
        self.col = get_books_collection()

    def find_by_id(self, book_id: str):
        doc = self.col.find_one({"id": book_id})
        return doc

    def search_by_title(self, keyword: str, limit: int = 10, skip: int = 0):
        # 最简单的模糊匹配
        cursor = self.col.find(
            {"title": {"$regex": keyword, "$options": "i"}}
        ).skip(skip).limit(limit)
        return list(cursor)
