"""
测试超时自动取消订单功能
"""
import time
import uuid
import pytest
import requests

from fe import conf
from fe.access.new_seller import register_new_seller
from fe.access.new_buyer import register_new_buyer
from fe.access import book as bookdb
from be.model.order_mongo import OrderMongo


class TestCancelTimeoutOrder:
    @pytest.fixture(autouse=True)
    def prepare(self):
        # 卖家
        self.seller_id = f"timeout_s_{uuid.uuid1()}"
        self.store_id = f"timeout_st_{uuid.uuid1()}"
        self.password = self.seller_id
        self.seller = register_new_seller(self.seller_id, self.password)
        assert self.seller.create_store(self.store_id) == 200

        # 买家
        self.buyer_id = f"timeout_b_{uuid.uuid1()}"
        self.buyer_pwd = self.buyer_id
        self.buyer = register_new_buyer(self.buyer_id, self.buyer_pwd)

        # 书
        bk = bookdb.BookDB(conf.Use_Large_DB).get_book_info(0, 1)[0]
        self.book_id = bk.id
        assert self.seller.add_book(self.store_id, 10, bk) == 200

        # 下单但不付款
        code, order_id = self.buyer.new_order(self.store_id, [(self.book_id, 1)])
        assert code == 200
        self.order_id = order_id

        yield

    def test_cancel_timeout_orders(self):
        """测试超时订单自动取消"""
        om = OrderMongo()
        
        # 手动设置订单创建时间为很久以前（模拟超时）
        from be.model.mongo_conn import get_db
        db = get_db()
        db["orders"].update_one(
            {"order_id": self.order_id},
            {"$set": {"created_time": int(time.time()) - 2000}}  # 2000秒前
        )
        
        # 执行超时取消（超时时间设为1800秒=30分钟）
        canceled_count = om.cancel_timeout_orders(timeout_seconds=1800)
        assert canceled_count >= 1
        
        # 验证订单状态已变为 canceled
        order = db["orders"].find_one({"order_id": self.order_id})
        assert order is not None
        assert order["status"] == "canceled"
        assert "cancel_reason" in order
        assert order["cancel_reason"] == "timeout"

