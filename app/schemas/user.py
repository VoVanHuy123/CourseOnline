from marshmallow import Schema, fields,post_dump
from sqlalchemy.orm import relationship, backref
from enum import Enum
from app.models.user import Gender
class UserRole(str, Enum):
    ADMIN = 'admin'
    STUDENT = 'student'
    TEACHER = 'teacher'

class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True, description= "Tên đăng nhập")
    password = fields.Str(required=True, metadata={"description": "Mật khẩu"},load_only=True)
    first_name = fields.Str(required=True)
    last_name = fields.Str(required=True)
    email = fields.Email()
    phonenumber = fields.Str()
    avatar = fields.Str()
    role = fields.Str()  # Không cần validate lại Enum ở đây
    is_validate = fields.Boolean()
    @post_dump
    def convert_enum_to_value(self, data, **kwargs):
        # Nếu role là Enum hoặc chuỗi bắt đầu bằng UserRole.
        role = data.get("role")
        if isinstance(role, str) and role.startswith("UserRole."):
            data["role"] = role.split(".")[1].lower()
        elif isinstance(role, UserRole):
            data["role"] = role.value
        return data
class TeacherSchema(UserSchema):
    current_workplace = fields.Str()
    degree = fields.Str()
class StudentSchema(UserSchema):
    student_code = fields.Str()
    university = fields.Str()
    gender = fields.Str()
    # gender = fields.Str(required=True, validate=lambda g: g in [g.value for g in Gender])

    

class UserCommentSchema(Schema):
    id = fields.Int(dump_only=True)
    first_name = fields.Str(required=True)
    last_name = fields.Str(required=True)
    avatar = fields.Str()
    
class UserLoginSchema(Schema):
    username = fields.Str(required=True, metadata={"description": "Tên đăng nhập"})
    password = fields.Str(required=True, metadata={"description": "Mật khẩu"},load_only=True)
class StudentRegisterSchema(Schema):
    username = fields.Str(required=True)
    password = fields.Str(required=True,load_only=True)
    first_name = fields.Str()
    last_name = fields.Str()
    email = fields.Email()
    phonenumber = fields.Str()
    role = fields.Str(required=True)  # student
    student_code = fields.Str(required=True)
    university = fields.Str(required=True)
    gender = fields.Str(required=True, validate=lambda g: g in [g.value for g in Gender])

class TeacherRegisterSchema(Schema):
    username = fields.Str(required=True)
    password = fields.Str(required=True,load_only=True)
    first_name = fields.Str()
    last_name = fields.Str()
    email = fields.Email()
    phonenumber = fields.Str()
    role = fields.Str(required=True)  # teacher
    current_workplace = fields.Str(required=True)
    degree = fields.Str(required=True)
class AdminRegisterSchema(Schema):
    username = fields.Str(required=True)
    password = fields.Str(required=True,load_only=True)
    first_name = fields.Str()
    last_name = fields.Str()
    role = fields.Str(required=True)  