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
    # role = fields.Str(validate=lambda x: x in UserRole)
    role = fields.Str()  # Không cần validate lại Enum ở đây

    

    @post_dump
    def convert_enum_to_value(self, data, **kwargs):
        if isinstance(data.get("role"), str) and data["role"].startswith("UserRole."):
            # Tách nếu bị serialize sai
            data["role"] = data["role"].split(".")[1].lower()
        return data

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