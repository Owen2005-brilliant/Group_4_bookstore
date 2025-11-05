from flask import Blueprint
from flask import request
from flask import jsonify
from be.model.buyer_mongo import BuyerMongo
from be.model.order_mongo import OrderMongo
from be.model.user_mongo import UserMongo

from be.model.buyer import Buyer
from be.model import user as user_model

bp_buyer = Blueprint("buyer", __name__, url_prefix="/buyer")

def check_token(user_id: str, token: str):
    um = UserMongo()
    ok, _ = um.check_token(user_id, token)
    return ok

@bp_buyer.route("/add_funds", methods=["POST"])
def add_funds():
    body = request.get_json()
    user_id = body.get("user_id")
    password = body.get("password")
    add_value = int(body.get("add_value", 0))

    bm = BuyerMongo()
    ok, msg = bm.add_funds(user_id, password, add_value)
    if not ok:
        #  根据md文件，401是授权失败，其它 5XX
        if msg == "authorization fail":
            return jsonify({"message": msg}), 401
        return jsonify({"message": msg}), 500
    return jsonify({"message": "ok"}), 200

@bp_buyer.route("/new_order", methods=["POST"])
def new_order():
    token = request.headers.get("token", "")
    body = request.get_json()
    user_id = body.get("user_id")
    store_id = body.get("store_id")
    books = body.get("books", [])

    if not check_token(user_id, token):
        return jsonify({"message": "authorization fail"}), 401

    bm = BuyerMongo()
    ok, msg, order_id = bm.new_order(user_id, store_id, books)
    if not ok:
        return jsonify({"message": msg}), 500
    return jsonify({"order_id": order_id}), 200


@bp_buyer.route("/payment", methods=["POST"])
def payment():
    body = request.get_json()
    user_id = body.get("user_id")
    order_id = body.get("order_id")
    password = body.get("password")

    bm = BuyerMongo()
    ok, msg = bm.payment(user_id, order_id, password)
    if not ok:
        if msg == "authorization fail":
            return jsonify({"message": msg}), 401
        return jsonify({"message": msg}), 500
    return jsonify({"message": "ok"}), 200


# 收货
@bp_buyer.route("/receive_order", methods=["POST"])
def receive_order():
    token = request.headers.get("token", "")
    body = request.get_json()
    user_id = body.get("user_id")
    order_id = body.get("order_id")

    if not check_token(user_id, token):
        return jsonify({"message": "authorization fail"}), 401

    om = OrderMongo()
    ok, msg = om.receive_order(user_id, order_id)
    if not ok:
        return jsonify({"message": msg}), 500
    return jsonify({"message": "ok"}), 200

# 查询我的订单
@bp_buyer.route("/list_orders", methods=["GET"])
def list_orders():
    token = request.headers.get("token", "")
    user_id = request.args.get("user_id", "")
    if not check_token(user_id, token):
        return jsonify({"message": "authorization fail"}), 401

    limit = int(request.args.get("limit", 20))
    skip = int(request.args.get("skip", 0))

    om = OrderMongo()
    orders = om.list_orders(user_id, limit=limit, skip=skip)
    return jsonify({"message": "ok", "orders": orders}), 200

# 取消订单
@bp_buyer.route("/cancel_order", methods=["POST"])
def cancel_order():
    token = request.headers.get("token", "")
    body = request.get_json()
    user_id = body.get("user_id")
    order_id = body.get("order_id")

    if not check_token(user_id, token):
        return jsonify({"message": "authorization fail"}), 401

    om = OrderMongo()
    ok, msg = om.cancel_order(user_id, order_id)
    if not ok:
        return jsonify({"message": msg}), 500
    return jsonify({"message": "ok"}), 200


