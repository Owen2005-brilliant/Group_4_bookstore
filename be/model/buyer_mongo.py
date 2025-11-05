
from be.model.mongo_conn import get_db
from be.model.user_mongo import UserMongo
import time
import uuid


class BuyerMongo:
    def __init__(self):
        self.db = get_db()
        # 用户表
        self.col_users = self.db["users"]
        # 店铺表（里面有店主 user_id）
        self.col_stores = self.db["stores"]
        self.col_store_books = self.db["store_books"]
        # 订单主表
        self.col_orders = self.db["orders"]
        # 订单明细表（一个订单多本书）
        self.col_order_items = self.db["order_items"]

    def new_order(self, user_id: str, store_id: str, books: list[dict]):
        """
        books 形如: [{"id": book_id, "count": 2}, ...]
        前端的 fe 测试就是这么发的
        返回: (True, "ok", order_id) 或 (False, "错误信息", "")
        """
        # 1. 用户存在吗
        user = self.col_users.find_one({"user_id": user_id})
        if not user:
            return False, "buyer not found", ""

        # 2. 店铺存在吗
        store = self.col_stores.find_one({"store_id": store_id})
        if not store:
            return False, "store not found", ""

        if not books:
            return False, "no books", ""

        # 3. 检查库存并算总价
        total_price = 0
        store_book_docs = []  # 跟 books 一一对齐，后面要扣库存
        for item in books:
            book_id = item.get("id")
            count = int(item.get("count", 0))
            if not book_id or count <= 0:
                return False, "invalid book item", ""

            sb = self.col_store_books.find_one(
                {"store_id": store_id, "book_id": book_id}
            )
            if not sb:
                return False, f"book {book_id} not found in store", ""
            if sb.get("stock_level", 0) < count:
                return False, f"stock not enough for book {book_id}", ""

            price = sb.get("price", 0)
            total_price += price * count
            store_book_docs.append(sb)

        # 4. 生成订单号
        order_id = f"order_{uuid.uuid4().hex}"

        # 5. 扣库存（下单就占库存，和很多参考答案是一样的做法）
        for sb, item in zip(store_book_docs, books):
            count = int(item["count"])
            self.col_store_books.update_one(
                {"_id": sb["_id"]},
                {"$inc": {"stock_level": -count}},
            )

        # 6. 写订单主表
        self.col_orders.insert_one(
            {
                "order_id": order_id,
                "buyer_id": user_id,
                "store_id": store_id,
                "status": "unpaid",
                "total_price": total_price,
                "created_time": int(time.time()),
            }
        )

        # 7. 写订单明细表
        order_items = []
        for item, sb in zip(books, store_book_docs):
            order_items.append(
                {
                    "order_id": order_id,
                    "book_id": item["id"],
                    "count": int(item["count"]),
                    "price": sb.get("price", 0),
                    "title": sb.get("title"),
                    "author": sb.get("author"),
                }
            )
        if order_items:
            self.col_order_items.insert_many(order_items)

        return True, "ok", order_id

    def payment(self, user_id: str, order_id: str, password: str):
        """
        支付逻辑：
        1. 找订单
        2. 校验买家
        3. 校验状态未支付
        4. 校验密码
        5. 买家扣钱
        6. 卖家收钱
        7. 订单状态改为 paid
        """
        order = self.col_orders.find_one({"order_id": order_id})
        if not order:
            return False, "order not found"

        if order.get("buyer_id") != user_id:
            return False, "authorization fail"

        if order.get("status") != "unpaid":
            return False, "order status invalid"

        # 校验密码
        um = UserMongo()
        ok, msg, _ = um.login(user_id, password, "tmp")
        if not ok:
            return False, "authorization fail"

        total_price = order.get("total_price", 0)

        # 买家扣款
        buyer = self.col_users.find_one({"user_id": user_id})
        if not buyer:
            return False, "buyer not found"

        if buyer.get("balance", 0) < total_price:
            return False, "not sufficient funds"

        self.col_users.update_one(
            {"user_id": user_id},
            {"$inc": {"balance": -total_price}},
        )

        # 卖家加钱
        store = self.col_stores.find_one({"store_id": order.get("store_id")})
        if store:
            seller_id = store.get("user_id")
            if seller_id:
                self.col_users.update_one(
                    {"user_id": seller_id},
                    {"$inc": {"balance": total_price}},
                )

        # 更新订单状态
        self.col_orders.update_one(
            {"order_id": order_id},
            {
                "$set": {
                    "status": "paid",
                    "pay_time": time.time(),
                }
            },
        )

        return True, "ok"

    def add_funds(self, user_id: str, password: str, add_value: int):
        """
        充值功能：
        1. 验证用户存在
        2. 验证密码
        3. 增加余额
        返回: (True, "ok") 或 (False, "错误信息")
        """
        # 1. 用户存在吗
        user = self.col_users.find_one({"user_id": user_id})
        if not user:
            return False, "authorization fail"

        # 2. 验证密码
        if user.get("password") != password:
            return False, "authorization fail"

        # 3. 增加余额
        self.col_users.update_one(
            {"user_id": user_id},
            {"$inc": {"balance": add_value}},
        )

        return True, "ok"
