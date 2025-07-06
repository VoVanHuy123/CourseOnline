from functools import wraps
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity,jwt_required,get_jwt
from werkzeug.exceptions import Unauthorized, Forbidden

def teacher_required(fn):
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        user_id = get_jwt_identity()  # lấy từ identity (sub)
        claims = get_jwt()  # lấy từ payload
        role = claims.get("role")

        if not user_id:
            raise Unauthorized(description="Không có token hoặc token không hợp lệ")

        if role != "teacher":
            raise Forbidden(description="Chỉ giáo viên mới được phép truy cập")

        return fn(*args, **kwargs)
    return wrapper
def admin_required(fn):
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        user_id = get_jwt_identity()  # lấy từ identity (sub)
        claims = get_jwt()  # lấy từ payload
        role = claims.get("role")

        if not user_id:
            raise Unauthorized(description="Không có token hoặc token không hợp lệ")

        if role != "admin":
            raise Forbidden(description="Chỉ admin mới được phép truy cập")

        return fn(*args, **kwargs)
    return wrapper