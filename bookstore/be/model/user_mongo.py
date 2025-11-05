import uuid
import time
from be.model.mongo_conn import get_db

class UserMongo:
    
    """
    专门管用户、token、密码的 Mongo 版本
    要和 JSON API 约定保持一致
    """
    def __init__(self):
        self.db = get_db()
        self.col = self.db["users"]
        # 单独放 token，便于多终端登录
        self.col_tokens = self.db["user_tokens"]

    # 注册
    def register(self, user_id: str, password: str):
        """
        返回 (ok: bool, msg: str)
        auth.py 里会把这个再转换成 200 / 5xx
        """
        if self.col.find_one({"user_id": user_id}):
            return False, "user exists"

        self.col.insert_one({
            "user_id": user_id,
            "password": password,
            "balance": 0,          # 给买家用的余额字段
            "create_time": int(time.time()),
        })
        return True, "ok"
    # 登录
    def login(self, user_id: str, password: str, terminal: str):
        u = self.col.find_one({"user_id": user_id})
        if not u:
            return False, "user not found", ""

        if u["password"] != password:
            return False, "password error", ""

        token = str(uuid.uuid4())
        now = int(time.time())

        self.col_tokens.update_one(
            {"user_id": user_id, "terminal": terminal},
            {
                "$set": {
                    "token": token,
                    "login_time": now,
                }
            },
            upsert=True,
        )
        return True, "ok", token

    # 校验 token
    def check_token(self, user_id: str, token: str, terminal: str | None = None):
        """
        给需要鉴权的地方用
        """
        query = {"user_id": user_id, "token": token}
        if terminal is not None:
            query["terminal"] = terminal

        t = self.col_tokens.find_one(query)
        if not t:
            return False, "invalid token"
        return True, "ok"
    # 登出
    def logout(self, user_id: str, token: str):
        # 先验证 token 是否存在且匹配
        ok, msg = self.check_token(user_id, token)
        if not ok:
            return False, msg
        
        # 验证通过后再删除
        res = self.col_tokens.delete_one({"user_id": user_id, "token": token})
        if res.deleted_count == 0:
            return False, "invalid token"
        return True, "ok"

    # 注销
    def unregister(self, user_id: str, password: str):
        """
        按说明文档：注销要校验密码
        """
        u = self.col.find_one({"user_id": user_id})
        if not u:
            return False, "user not found"
        if u["password"] != password:
            return False, "password error"

        # 删 token
        self.col_tokens.delete_many({"user_id": user_id})
        # 删用户
        self.col.delete_one({"user_id": user_id})
        return True, "ok"

    # 修改密码
    def change_password(self, user_id: str, old_password: str, new_password: str, token: str = None):
        """
        如果提供了 token，就验证 token；否则只验证旧密码
        """
        # 如果提供了 token，先验证 token（token 可能是空字符串，需要检查）
        if token is not None and token != "":
            ok, msg = self.check_token(user_id, token)
            if not ok:
                return False, msg

        u = self.col.find_one({"user_id": user_id})
        if not u:
            return False, "user not found"
        if u["password"] != old_password:
            return False, "password error"

        self.col.update_one(
            {"user_id": user_id},
            {"$set": {"password": new_password}}
        )
        return True, "ok"
    
    def add_funds(self, user_id: str, amount: int):
        """
        有些人会把充值写在 buyer 里，你写在 user 里也行
        """
        res = self.col.update_one(
            {"user_id": user_id},
            {"$inc": {"balance": amount}}
        )
        if res.matched_count == 0:
            return False, "user not found"
        return True, "ok"
