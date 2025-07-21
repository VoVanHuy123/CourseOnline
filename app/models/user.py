from sqlalchemy.orm import relationship, backref
from sqlalchemy import Column, Enum, Integer, String,Boolean,ForeignKey
from flask_login import UserMixin
from .base import BaseModel
import enum
from werkzeug.security import generate_password_hash, check_password_hash


class UserRole(enum.Enum):
    ADMIN = 'admin'
    STUDENT = 'student'
    TEACHER = 'teacher'

class User(BaseModel,UserMixin):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    username = Column(String(50),nullable=False,unique=True)
    password = Column(String(256),nullable=False)
    first_name = Column(String(50),nullable=False)
    last_name = Column(String(50),nullable=False)
    email = Column(String(50),nullable=True,unique=True)
    phonenumber = Column(String(15),nullable=True,unique=True)
    role = Column(Enum(UserRole, native_enum=False), nullable=False)
    avatar = Column(String(225),nullable=True)
    is_validate = Column(Boolean,default=False)
    __mapper_args__ = {
        'polymorphic_identity': 'user',
        'polymorphic_on': role 
    }


    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


class Teacher(User):
    __tablename__ = 'teacher'
    __mapper_args__ = {
        'polymorphic_identity': UserRole.TEACHER
    }
    id = Column(Integer, ForeignKey('user.id'), primary_key=True)
    current_workplace = Column(String(100),nullable=True)
    degree = Column(String(100), nullable=True) 

class Gender(enum.Enum):
    MALE = 'male'
    FEMALE = 'female'
    ORTHER = 'orther'

class Student(User):
    __tablename__ = 'student'
    __mapper_args__ = {
        'polymorphic_identity': UserRole.STUDENT
    }
    id = Column(Integer, ForeignKey('user.id'), primary_key=True)
    student_code = Column(String(25),nullable=False)
    university = Column(String(50),nullable=False)
    gender = Column(Enum(Gender, native_enum=False, values_callable=lambda x: [e.value for e in x]), nullable=False)

    enrollments = relationship('Enrollment', backref='student', lazy=True, cascade='all, delete-orphan',passive_deletes=True)
    lesson_progress = relationship('LessonProgress', backref='student', lazy=True, cascade='all, delete-orphan',passive_deletes=True)
    reviews = relationship('CourseReview', backref='student', lazy=True, cascade='all, delete-orphan',passive_deletes=True)
class Admin(User):
    __tablename__ = 'admin'
    __mapper_args__ = {
        'polymorphic_identity': UserRole.ADMIN
    }
    id = Column(Integer, ForeignKey('user.id'), primary_key=True)