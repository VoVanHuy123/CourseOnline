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
def student_required(fn):
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        user_id = get_jwt_identity()  # lấy từ identity (sub)
        claims = get_jwt()  # lấy từ payload
        role = claims.get("role")

        if not user_id:
            raise Unauthorized(description="Không có token hoặc token không hợp lệ")

        if role != "student":
            raise Forbidden(description="Chỉ student mới được phép truy cập")

        return fn(*args, **kwargs)
    return wrapper
def login_required(fn):
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        user_id = get_jwt_identity()  # lấy từ identity (sub)
        claims = get_jwt()  # lấy từ payload

        if not user_id:
            raise Unauthorized(description="Không có token hoặc token không hợp lệ")

        return fn(*args, **kwargs)
    return wrapper

from functools import wraps
from flask_jwt_extended import get_jwt_identity, jwt_required
from werkzeug.exceptions import Forbidden
from flask import request

def owner_required(model, user_field="user_id", lookup_arg="id"):# ví dụ update_review(review_id, **kwargs): thì lookup_arg = "review_id"
    def decorator(fn):                                      
        @wraps(fn)
        @jwt_required()
        def wrapper(*args, **kwargs):
            user_id = get_jwt_identity()
            obj_id = kwargs.get(lookup_arg)

            if obj_id is None:
                raise Forbidden("Không tìm thấy ID đối tượng để kiểm tra quyền")

            # Truy vấn model để lấy đối tượng
            obj = model.query.get(obj_id)
            if not obj:
                raise Forbidden("Không tìm thấy đối tượng")

            # So sánh quyền sở hữu
            if getattr(obj, user_field) != user_id:
                raise Forbidden("Bạn không có quyền truy cập tài nguyên này")

            return fn(*args, **kwargs)
        return wrapper
    return decorator
