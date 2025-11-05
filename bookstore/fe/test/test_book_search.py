import pytest
import requests
from fe import conf
from fe.access.new_seller import register_new_seller
from fe.access import book as bookdb
import uuid


class TestBookSearch:
    @pytest.fixture(autouse=True)
    def prepare(self):
        # 先随便查一条书，用它的 title 做搜索词
        db = bookdb.BookDB(conf.Use_Large_DB)
        bk = db.get_book_info(0, 1)[0]
        self.sample_title = bk.title.split(" ")[0] or bk.title
        # 建一个店，放这本书，方便测试店铺内搜索
        self.seller_id = f"search_s_{uuid.uuid1()}"
        self.store_id = f"search_store_{uuid.uuid1()}"
        self.password = self.seller_id
        self.seller = register_new_seller(self.seller_id, self.password)
        assert self.seller.create_store(self.store_id) == 200
        assert self.seller.add_book(self.store_id, 5, bk) == 200
        yield

    def test_search_global(self):
        url = f"{conf.URL}/book/search"
        resp = requests.get(url, params={"q": self.sample_title, "limit": 5})
        assert resp.status_code == 200
        data = resp.json()
        assert "books" in data

    def test_search_in_store(self):
        url = f"{conf.URL}/book/search"
        resp = requests.get(
            url,
            params={
                "q": self.sample_title,
                "store_id": self.store_id,
                "limit": 5,
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        # 至少能搜到刚刚那个
        assert any(b["store_id"] == self.store_id for b in data["books"])
