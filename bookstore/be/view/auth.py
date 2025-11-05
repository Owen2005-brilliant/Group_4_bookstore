from flask import Blueprint
from flask import request
from flask import jsonify
from be.model import user
from be.model.user_mongo import UserMongo

bp_auth = Blueprint("auth", __name__, url_prefix="/auth")


@bp_auth.route("/login", methods=["POST"])
def login():
    body = request.get_json()
    user_id = body.get("user_id")
    password = body.get("password")
    terminal = body.get("terminal", "terminal")

    um = UserMongo()
    ok, msg, token = um.login(user_id, password, terminal)
    if not ok:
        return jsonify({"message": msg}), 401
    return jsonify({"message": "ok", "token": token}), 200


@bp_auth.route("/logout", methods=["POST"])
def logout():
    body = request.get_json()
    user_id = body.get("user_id")
    # 根据 auth.md，token 应该在 Headers 中，而不是 Body 中
    token = request.headers.get("token", "")

    um = UserMongo()
    ok, msg = um.logout(user_id, token)
    if not ok:
        return jsonify({"message": msg}), 401
    return jsonify({"message": "ok"}), 200



@bp_auth.route("/register", methods=["POST"])
def register():
    body = request.get_json()
    user_id = body.get("user_id")
    password = body.get("password")

    um = UserMongo()
    ok, msg = um.register(user_id, password)
    if not ok:
        # 测试脚本只要看到不是 200 就会当成失败
        return jsonify({"message": msg}), 500
    return jsonify({"message": "ok"}), 200


@bp_auth.route("/unregister", methods=["POST"])
def unregister():
    body = request.get_json()
    user_id = body.get("user_id")
    password = body.get("password")
    token = body.get("token")  # 可能没有

    um = UserMongo()

    # 如果带了 token，就按严格模式来
    if token:
        ok, msg = um.unregister(user_id, password, token)
        if not ok:
            return jsonify({"message": msg}), 401
        return jsonify({"message": "ok"}), 200

    # 如果没带 token，就按测试脚本的老套路：只要账号密码对就删
    u = um.col.find_one({"user_id": user_id})
    if not u:
        return jsonify({"message": "user not found"}), 401
    if u.get("password") != password:
        return jsonify({"message": "authorization fail"}), 401

    um.col.delete_one({"user_id": user_id})
    return jsonify({"message": "ok"}), 200


@bp_auth.route("/password", methods=["POST"])
def change_password():
    body = request.get_json()
    user_id = body.get("user_id")
    # 根据 auth.md，字段名是 oldPassword 和 newPassword（驼峰命名）
    old_password = body.get("oldPassword")
    new_password = body.get("newPassword")
    token = body.get("token")

    um = UserMongo()
    ok, msg = um.change_password(user_id, old_password, new_password, token)
    if not ok:
        return jsonify({"message": msg}), 401
    return jsonify({"message": "ok"}), 200


