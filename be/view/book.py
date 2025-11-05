from flask import Blueprint, request, jsonify
from be.model.mongo_conn import get_db

bp_book = Blueprint("book", __name__, url_prefix="/book")

@bp_book.route("/search", methods=["GET"])
def search_book():
    keyword = request.args.get("q", "").strip()
    store_id = request.args.get("store_id")  
    limit = int(request.args.get("limit", 10))
    skip = int(request.args.get("skip", 0))

    db = get_db()

    if store_id:
        cond = {"store_id": store_id}
        if keyword:
            cond["title"] = {"$regex": keyword, "$options": "i"}
        cursor = db["store_books"].find(cond).skip(skip).limit(limit)
        docs = list(cursor)
        for d in docs:
            d["_id"] = str(d["_id"])
        return jsonify({"message": "ok", "count": len(docs), "books": docs}), 200

    # 搜全站 books
    col = db["books"]
    if keyword:
        # 先尝试使用全文索引搜索（支持 title, author, book_intro, tags, content）
        try:
            docs = list(
                col.find({"$text": {"$search": keyword}})
                   .skip(skip).limit(limit)
            )
        except Exception:
            docs = []
        
        # 如果全文索引不可用或没有结果，使用正则表达式搜索多个字段
        if not docs:
            # 使用 $or 搜索多个字段：题目、标签、目录、内容
            docs = list(
                col.find({
                    "$or": [
                        {"title": {"$regex": keyword, "$options": "i"}},
                        {"tags": {"$regex": keyword, "$options": "i"}},
                        {"book_intro": {"$regex": keyword, "$options": "i"}},
                        {"content": {"$regex": keyword, "$options": "i"}},
                        {"author": {"$regex": keyword, "$options": "i"}},
                    ]
                }).skip(skip).limit(limit)
            )
    else:
        docs = list(col.find().skip(skip).limit(limit))

    for d in docs:
        d["_id"] = str(d["_id"])
    return jsonify({"message": "ok", "count": len(docs), "books": docs}), 200