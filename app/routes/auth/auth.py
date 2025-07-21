from flask import Blueprint, jsonify, request
from flask_apispec import use_kwargs, marshal_with, doc
from flask_jwt_extended import create_access_token
from app.schemas.user import UserLoginSchema,UserSchema,TeacherRegisterSchema,StudentRegisterSchema,AdminRegisterSchema
from app.extensions import login_manager,db
from app.models.user import User,Student,Teacher,Admin
from werkzeug.security import generate_password_hash
from marshmallow import  ValidationError
from flask_jwt_extended import jwt_required,get_jwt_identity
from app.models.user import Student, Teacher, UserRole
from datetime import timedelta


import traceback

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/login', methods=['POST'])
@doc(description="Đăng nhập và nhận access token", tags=["Auth"])
@use_kwargs(UserLoginSchema, location="json")
def login(username, password):
    user = User.query.filter_by(username=username).first()
    print(user)
    if not user :
        return {"msg": "Sai username","field":"username"}, 401
    if not user.check_password(password):
        return {"msg": "Sai mật khẩu","field":"password"}, 401
    access_token = create_access_token(
    identity=str(user.id), 
    additional_claims={"role": user.role.value}
    )
    user_data  = UserSchema().dump(user)
    # return jsonify(access_token=access_token)
    return {"user":user_data ,"access_token": access_token},200



@auth_bp.route('/register', methods=['POST'])
@doc(description="Đăng ký tài khoản", tags=["Auth"])
def register():
    try:
        data = request.get_json()
        role = data.get("role")
        if role == "student":
            schema = StudentRegisterSchema()
            validated_data = schema.load(data)
            user = Student(
                username=validated_data["username"],
                password=generate_password_hash(validated_data["password"]),
                first_name=validated_data.get("first_name"),
                last_name=validated_data.get("last_name"),
                email=validated_data.get("email"),
                phonenumber=validated_data.get("phonenumber"),
                student_code=validated_data.get("student_code"),
                university=validated_data.get("university"),
                gender=validated_data.get("gender"),
                role=UserRole.STUDENT.value,
                is_validate=True
            )

        elif role == "teacher":
            schema = TeacherRegisterSchema()
            validated_data = schema.load(data)
            user = Teacher(
                username=validated_data["username"],
                password=generate_password_hash(validated_data["password"]),
                first_name=validated_data.get("first_name"),
                last_name=validated_data.get("last_name"),
                email=validated_data.get("email"),
                phonenumber=validated_data.get("phonenumber"),
                current_workplace=validated_data.get("current_workplace"),
                degree=validated_data.get("degree"),
                role=UserRole.TEACHER.value,
                is_validate=False
            )
        elif role == "admin":
            schema = AdminRegisterSchema()
            validated_data = schema.load(data)
            user = Admin(
                username=validated_data["username"],
                password=generate_password_hash(validated_data["password"]),
                first_name=validated_data.get("first_name"),
                last_name=validated_data.get("last_name"),
                role=UserRole.ADMIN.value,
                is_validate=True
            )
        else:
            return {"msg": "Vai trò không hợp lệ"}, 400  

        # Check trùng username
        if User.query.filter_by(username=user.username).first():
            return {"msg": "Tên đăng nhập đã tồn tại"}, 400 

        db.session.add(user)
        db.session.commit()

        return {"msg": "Đăng ký thành công!"}, 201 

    except ValidationError as ve:
        return {"msg": ve.messages}, 422  

    except Exception as e:
        traceback.print_exc()
        return {"msg": "Lỗi hệ thống", "error": str(e)}, 500 



@login_manager.user_loader
def user_load(user_id):
    # return get_user_account_by_id(user_id)
    return User.query.get(int(user_id))

# Flask‑JWT‑Extended
@auth_bp.route('/refresh', methods=['POST'])
@doc(description="Làm mới tài khoản", tags=["Auth"])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity, expires_delta=timedelta(minutes=10))
    return jsonify(access=access_token)

#đăng kí các hàm ở đây để hiện lên swagger
def user_register_docs(docs):
    docs.register(login, blueprint='auth')
    docs.register(register, blueprint='auth')
    docs.register(refresh, blueprint='auth')