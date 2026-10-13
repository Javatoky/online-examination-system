from functools import wraps

from flask_jwt_extended import get_jwt, jwt_required

from .responses import fail


def role_required(*roles):
    """按角色限制接口访问，需与 JWT 中的 role 声明匹配。"""

    def decorator(fn):
        @wraps(fn)
        @jwt_required()
        def wrapper(*args, **kwargs):
            if get_jwt().get("role") not in roles:
                return fail("无权限访问该资源", http_status=403)
            return fn(*args, **kwargs)

        return wrapper

    return decorator


def current_claims():
    return get_jwt()
