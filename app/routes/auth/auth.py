from flask import Blueprint, jsonify, request
from flask_apispec import use_kwargs, marshal_with, doc
from flask_jwt_extended import create_access_token
from app.schemas.user import StudentSchema, TeacherSchema, UserLoginSchema,UserSchema,TeacherRegisterSchema,StudentRegisterSchema,AdminRegisterSchema
from app.extensions import login_manager,db
from app.models.user import User,Student,Teacher,Admin
from werkzeug.security import generate_password_hash
from marshmallow import  ValidationError
from flask_jwt_extended import jwt_required,get_jwt_identity
from app.models.user import Student, Teacher, UserRole
from datetime import timedelta
from app.perms.perms import admin_required,login_required,owner_required,owner_or_admin_required

import traceback
import cloudinary.uploader 


import traceback

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/login', methods=['POST'])
@doc(description="Đăng nhập và nhận access token", tags=["Auth"])
@use_kwargs(UserLoginSchema, location="json")
# @marshal_with(UserSchema)
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

@auth_bp.route('/teachers/unverified', methods=['GET'])
@doc(description="Lấy danh sách giáo viên chưa xác thực", tags=["Teacher"])
@marshal_with(TeacherSchema(many=True))
@admin_required
def get_unverified_teachers():
    unverified_teachers = Teacher.query.filter_by(is_validate=False).all()
    return unverified_teachers
@auth_bp.route('/teachers/validate/<int:teacher_id>', methods=['PUT'])
@doc(description="Xác thực giáo viên (is_validate = true)", tags=["Teacher"])
@admin_required
def validate_teacher(teacher_id):
    teacher = Teacher.query.get(teacher_id)
    if not teacher:
        return {"msg": "Không tìm thấy giáo viên"}, 404
    
    if teacher.is_validate:
        return {"msg": "Giáo viên đã được xác thực"}, 400

    teacher.is_validate = True
    db.session.commit()
    return {"msg": "Xác thực thành công"}, 200


@auth_bp.route('/students/<int:student_id>', methods=['GET'])
@doc(description="Lấy thông tin sinh viên theo ID", tags=["Student"])
@marshal_with(StudentRegisterSchema)
@login_required
def get_student(student_id):
    student = Student.query.get(student_id)
    if not student:
        return {"msg": "Không tìm thấy sinh viên"}, 404
    return student

 # đảm bảo bạn đã cấu hình cloudinary

@auth_bp.route('/students/<int:student_id>', methods=['PATCH'])
@doc(description="Cập nhật thông tin sinh viên", tags=["Student"])
@owner_or_admin_required(model=Student, user_field="id", lookup_arg="student_id")
@marshal_with(StudentSchema)
def update_student(student_id):
    student = Student.query.get(student_id)
    if not student:
        return {"msg": "Không tìm thấy sinh viên"}, 404

    try:
        data = request.form
        avatar_file = request.files.get("avatar")

        # Cập nhật thông tin cá nhân
        if "first_name" in data:
            student.first_name = data["first_name"]
        if "last_name" in data:
            student.last_name = data["last_name"]
        if "email" in data:
            student.email = data["email"]
        if "phonenumber" in data:
            student.phonenumber = data["phonenumber"]
        if "student_code" in data:
            student.student_code = data["student_code"]
        if "university" in data:
            student.university = data["university"]
        if "gender" in data:
            gender_value = data["gender"]
            if "." in gender_value:
                gender_value = gender_value.split(".")[1].lower()
            student.gender = gender_value

        # Xử lý avatar
        # if "null_avatar" in data:
        #     student.avatar = None
        elif avatar_file:
            result = cloudinary.uploader.upload(avatar_file)
            student.avatar = result["secure_url"]

        db.session.commit()
        return student, 200
        # return {"msg": "Cập nhật thông tin sinh viên thành công"}, 200

    except Exception as e:
        traceback.print_exc()
        return {"msg": "Lỗi hệ thống", "error": str(e)}, 500


@auth_bp.route('/teachers/<int:teacher_id>', methods=['GET'])
@doc(description="Lấy thông tin giáo viên theo ID", tags=["Teacher"])
@marshal_with(TeacherSchema)
@login_required
def get_teacher(teacher_id):
    teacher = Teacher.query.get(teacher_id)
    if not teacher:
        return {"msg": "Không tìm thấy giáo viên"}, 404
    return teacher
@auth_bp.route('/teachers/<int:teacher_id>', methods=['PATCH'])
@doc(description="Cập nhật thông tin giáo viên", tags=["Teacher"])
@owner_or_admin_required(model=Teacher, user_field="id", lookup_arg="teacher_id")
@marshal_with(TeacherSchema)
def update_teacher(teacher_id):
    teacher = Teacher.query.get(teacher_id)
    if not teacher:
        return {"msg": "Không tìm thấy giáo viên"}, 404

    try:
        data = request.form  # để xử lý multipart/form-data
        avatar_file = request.files.get("avatar")

        # Cập nhật các trường cơ bản
        if "first_name" in data:
            teacher.first_name = data["first_name"]
        if "last_name" in data:
            teacher.last_name = data["last_name"]
        if "email" in data:
            teacher.email = data["email"]
        if "phonenumber" in data:
            teacher.phonenumber = data["phonenumber"]
        if "current_workplace" in data:
            teacher.current_workplace = data["current_workplace"]
        if "degree" in data:
            teacher.degree = data["degree"]

        # Cập nhật avatar nếu có
        if avatar_file:
            result = cloudinary.uploader.upload(avatar_file)
            teacher.avatar = result["secure_url"]

        if "null_avatar" in data :
            teacher.avatar = None

        db.session.commit()
        # return {"msg": "Cập nhật thông tin thành công"}, 200
        return teacher, 200

    except Exception as e:
        traceback.print_exc()
        return {"msg": "Lỗi hệ thống", "error": str(e)}, 500




#đăng kí các hàm ở đây để hiện lên swagger
def user_register_docs(docs):
    docs.register(login, blueprint='auth')
    docs.register(register, blueprint='auth')
    docs.register(refresh, blueprint='auth')
    docs.register(get_unverified_teachers, blueprint='auth')
    docs.register(validate_teacher, blueprint='auth')
    docs.register(get_student, blueprint='auth')
    docs.register(update_student, blueprint='auth')
    docs.register(get_teacher, blueprint='auth')
    docs.register(update_teacher, blueprint='auth')