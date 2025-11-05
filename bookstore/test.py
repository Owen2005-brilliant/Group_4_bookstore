from be.model.book_mongo import BookMongo

bm = BookMongo()
print(bm.find_by_id("1"))               # 看看能不能查到一条
print(bm.search_by_title("数据", 5))     # 看看能不能查到几条
