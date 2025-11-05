import time
from be.model.mongo_conn import get_db

class OrderMongo:
    def __init__(self):
        self.db = get_db()
        self.col_orders = self.db["orders"]
        self.col_order_items = self.db["order_items"]

    # 卖家发货：paid → delivering
    def deliver_order(self, store_id: str, order_id: str):
        order = self.col_orders.find_one({"order_id": order_id})
        if not order:
            return False, "order not found"
        if order["store_id"] != store_id:
            return False, "order not belong to this store"
        if order["status"] != "paid":
            return False, "order status not paid"

        self.col_orders.update_one(
            {"order_id": order_id},
            {"$set": {"status": "delivering", "deliver_time": int(time.time())}}
        )
        return True, "ok"

    # 买家收货：delivering → received
    def receive_order(self, buyer_id: str, order_id: str):
        order = self.col_orders.find_one({"order_id": order_id})
        if not order:
            return False, "order not found"
        if order["buyer_id"] != buyer_id:
            return False, "order not belong to user"
        if order["status"] != "delivering":
            return False, "order status not delivering"

        self.col_orders.update_one(
            {"order_id": order_id},
            {"$set": {"status": "received", "receive_time": int(time.time())}}
        )
        return True, "ok"

    # 买家查询订单列表
    def list_orders(self, buyer_id: str, limit: int = 20, skip: int = 0):
        cursor = self.col_orders.find(
            {"buyer_id": buyer_id}
        ).sort("created_time", -1).skip(skip).limit(limit)
        orders = list(cursor)

        # 附带上订单明细
        for od in orders:
            items = list(self.col_order_items.find({"order_id": od["order_id"]}))
            od["items"] = items
            od["_id"] = str(od["_id"])
            for it in od["items"]:
                it["_id"] = str(it["_id"])
        return orders

    # 买家取消订单
    def cancel_order(self, buyer_id: str, order_id: str):
        order = self.col_orders.find_one({"order_id": order_id})
        if not order:
            return False, "order not found"
        if order["buyer_id"] != buyer_id:
            return False, "order not belong to user"
        if order["status"] not in ("unpaid", "paid"):
            # 发货后就不让买家直接取消了
            return False, "order status not cancelable"

        self.col_orders.update_one(
            {"order_id": order_id},
            {"$set": {"status": "canceled", "cancel_time": int(time.time())}}
        )
        return True, "ok"

    def cancel_timeout_orders(self, timeout_seconds: int = 1800):
        now_ts = int(time.time())
        expire_ts = now_ts - timeout_seconds
        # 找到超时且还未支付的订单
        res = self.col_orders.update_many(
            {
                "status": "unpaid",
                "created_time": {"$lt": expire_ts}
            },
            {
                "$set": {
                    "status": "canceled",
                    "cancel_time": now_ts,
                    "cancel_reason": "timeout"
                }
            }
        )
        return res.modified_count
