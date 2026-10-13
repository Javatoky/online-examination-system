"""P1 登录验证：核对用户名/密码并签发 JWT。"""

from flask import Blueprint, request
from flask_jwt_extended import create_access_token, get_jwt, jwt_required
from werkzeug.security import check_password_hash

from ..models import Admin, Student, Teacher
from ..utils.responses import fail, ok

bp = Blueprint("auth", __name__)

# 三类角色的账户表（D1 用户信息）
ROLE_TABLES = {"admin": Admin, "teacher": Teacher, "student": Student}


@bp.post("/auth/login")
def login():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""
    if not username or not password:
        return fail("用户名和密码不能为空")

    for role, model in ROLE_TABLES.items():
        user = model.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            uid = getattr(user, f"{role}_id")
            name = getattr(user, f"{role}_name", None) or "系统管理员"
            token = create_access_token(
                identity=str(uid),
                additional_claims={"role": role, "uid": uid, "username": username, "name": name},
            )
            return ok(
                {
                    "token": token,
                    "role": role,
                    "uid": uid,
                    "username": username,
                    "name": name,
                }
            )
    return fail("用户名或密码错误", http_status=401)


@bp.get("/auth/me")
@jwt_required()
def me():
    claims = get_jwt()
    return ok(
        {
            "role": claims.get("role"),
            "uid": claims.get("uid"),
            "username": claims.get("username"),
            "name": claims.get("name"),
        }
    )
