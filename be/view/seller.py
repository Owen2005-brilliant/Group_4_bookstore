from flask import Blueprint
from flask import request
from flask import jsonify
from be.model import seller
from be.model.store_mongo import StoreMongo
from be.model.order_mongo import OrderMongo
from be.model.user_mongo import UserMongo
from be.model import user 
import json

bp_seller = Blueprint("seller", __name__, url_prefix="/seller")

def check_token(user_id: str, token: str):
    um = UserMongo()
    ok, _ = um.check_token(user_id, token)
    return ok

# 1) 创建商铺
@bp_seller.route("/create_store", methods=["POST"])
def create_store():
    body = request.get_json()
    token = request.headers.get("token", "")

    user_id = body.get("user_id")
    store_id = body.get("store_id")

    # 规范要求要校验 token
    if not check_token(user_id, token):
        return jsonify({"message": "authorization fail"}), 401

    sm = StoreMongo()
    ok, msg = sm.create_store(store_id, user_id)
    if not ok:
        return jsonify({"message": msg}), 500
    return jsonify({"message": "ok"}), 200


@bp_seller.route("/add_book", methods=["POST"])
def add_book():
    body = request.get_json()
    token = request.headers.get("token", "")

    user_id = body.get("user_id")
    store_id = body.get("store_id")
    book_info = body.get("book_info")  # 规范要求整个对象
    stock_level = int(body.get("stock_level", 0))

    if not check_token(user_id, token):
        return jsonify({"message": "authorization fail"}), 401

    if not book_info or "id" not in book_info:
        return jsonify({"message": "invalid book_info"}), 500

    book_id = book_info["id"]
    price = int(book_info.get("price", 0))

    sm = StoreMongo()
    ok, msg = sm.add_book_to_store_with_info(
        store_id=store_id,
        book_info=book_info,
        price=price,
        stock_level=stock_level
    )
    if not ok:
        return jsonify({"message": msg}), 500
    return jsonify({"message": "ok"}), 200


@bp_seller.route("/add_stock_level", methods=["POST"])
def add_stock_level():
    body = request.get_json()
    token = request.headers.get("token", "")

    user_id = body.get("user_id")
    store_id = body.get("store_id")
    book_id = body.get("book_id")
    add_stock_level = int(body.get("add_stock_level", 0))

    if not check_token(user_id, token):
        return jsonify({"message": "authorization fail"}), 401

    sm = StoreMongo()
    ok, msg = sm.add_stock_level(store_id, book_id, add_stock_level)
    if not ok:
        return jsonify({"message": msg}), 500
    return jsonify({"message": "ok"}), 200

@bp_seller.route("/deliver_order", methods=["POST"])
def deliver_order():
    token = request.headers.get("token", "")
    body = request.get_json()

    user_id = body.get("user_id")
    store_id = body.get("store_id")
    order_id = body.get("order_id")

    if not check_token(user_id, token):
        return jsonify({"message": "authorization fail"}), 401

    om = OrderMongo()
    ok, msg = om.deliver_order(store_id, order_id)
    if not ok:
        return jsonify({"message": msg}), 500
    return jsonify({"message": "ok"}), 200
