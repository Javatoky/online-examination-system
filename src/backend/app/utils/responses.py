from flask import jsonify


def ok(data=None, msg="成功"):
    return jsonify({"code": 0, "msg": msg, "data": data})


def fail(msg="请求失败", http_status=400, code=1):
    return jsonify({"code": code, "msg": msg, "data": None}), http_status
