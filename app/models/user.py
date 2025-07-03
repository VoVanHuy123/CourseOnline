from sqlalchemy.orm import relationship, backref
from sqlalchemy import Column, Enum, Integer, String
from flask_login import UserMixin
from .base import BaseModel
import enum

class UserRole(enum.Enum):
    ADMIN = 'admin'
    STUDENT = 'student'
    TEACHER = 'teacher'

class User(BaseModel,UserMixin):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    username = Column(String(50),nullable=False,unique=True)
    password = Column(String(50),nullable=False)
    first_name = Column(String(50),nullable=False)
    last_name = Column(String(50),nullable=False)
    email = Column(String(50),nullable=True,unique=True)
    phonenumber = Column(String(15),nullable=True,unique=True)
    role = Column(Enum(UserRole),nullable=False)
    __mapper_args__ = {
        'polymorphic_identity': 'user',
        'polymorphic_on': role 
    }


class Teacher(User):
    __tablename__ = 'teacher'
    __mapper_args__ = {
        'polymorphic_identity': UserRole.TEACHER
    }
    current_workplace = Column(String(100))
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

    student_code = Column(String(25),nullable=False)
    university = Column(String(50),nullable=False)
    gender = Column(Enum(Gender),nullable=False)

    enrollments = relationship('Enrollment', backref='student', lazy=True)
    lesson_progress = relationship('LessonProgress', backref='student', lazy=True)
    reviews = relationship('CourseReview', backref='student', lazy=True)