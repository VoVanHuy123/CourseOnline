from sqlalchemy.orm import relationship, backref
from sqlalchemy import Column, Enum, Integer, Float, String, Boolean, ForeignKey,Text
from .base import BaseModel
import enum

class Category(BaseModel):
    id = Column(Integer,primary_key=True)
    name = Column(String(50),nullable=False)

class Course(BaseModel):
    id = Column(Integer, primary_key=True)
    title = Column(String(100),nullable=False)
    description = Column(Text)
    price = Column(Float,nullable=False)
    image = Column(String(255),nullable=True)
    teacher_id = Column(Integer, ForeignKey('user.id'))
    category_id = Column(Integer, ForeignKey('category.id'))
    is_sequential = Column(Boolean, default=False)
    is_public = Column(Boolean,default=False)

    chapters = relationship('Chapter', backref='course', lazy=True , cascade='all, delete-orphan')
    enrollments = relationship('Enrollment', backref='course', lazy=True, cascade='all, delete-orphan')
    reviews = relationship('CourseReview', backref='course', lazy=True, cascade='all, delete-orphan')

    

class Chapter(BaseModel):
    id = Column(Integer, primary_key=True)
    title = Column(String(100))
    description = Column(Text)
    order = Column(Integer)

    course_id = Column(Integer, ForeignKey('course.id',ondelete="CASCADE"))

    lessons = relationship('Lesson', backref='chapter', lazy=True,cascade='all, delete-orphan')

class Type(enum.Enum):
    TEXT = "text"
    VIDEO = 'video'
    FILE = "file"
    IMAGE = "image"

class Lesson(BaseModel):
    id = Column(Integer, primary_key=True)
    title = Column(String(100))
    description = Column(Text)
    type = Column(Enum(Type))  # 'text', 'video', 'pdf', ...
    content_url = Column(String(255))
    image = Column(String(255),nullable=True)
    is_published = Column(Boolean, default=False)
    order = Column(Integer)
    is_locked = Column(Boolean, default=True)

    chapter_id = Column(Integer, ForeignKey('chapter.id',ondelete="CASCADE"))

    comments = relationship('LessonComment', backref='lesson', lazy=True , cascade='all, delete-orphan')

class LessonComment(BaseModel):
    id = Column(Integer, primary_key=True)
    content = Column(Text)
    reply_to = Column(Integer, ForeignKey('lesson_comment.id'), nullable=True)

    user_id = Column(Integer, ForeignKey('user.id',ondelete="CASCADE"))
    lesson_id = Column(Integer, ForeignKey('lesson.id',ondelete="CASCADE"))
    
    replies = relationship('LessonComment', backref=backref('parent', remote_side=[id]), lazy=True,cascade='all, delete-orphan', single_parent=True )

# comment.replies: lấy danh sách các phản hồi (con) của comment này.
# reply.parent: lấy comment gốc (cha) của phản hồi này.

class Status(enum.Enum):
    COMPLETED = 'completed'
    UNFINISHED ='unfinished'
class Enrollment(BaseModel):
    id = Column(Integer, primary_key=True)
    progress = Column(Float, default=0.0)
    status = Column(Enum(Status, native_enum=False, values_callable=lambda x: [e.value for e in x]), default=Status.UNFINISHED)
    payment_status = Column(Boolean, default=False)
    order_id = Column(String(100), nullable=True)

    user_id = Column(Integer, ForeignKey('user.id',ondelete="CASCADE"))
    course_id = Column(Integer, ForeignKey('course.id',ondelete="CASCADE"))

class LessonProgress(BaseModel):
    id = Column(Integer, primary_key=True)
    is_completed = Column(Boolean, default=False)

    user_id = Column(Integer, ForeignKey('user.id',ondelete="CASCADE"))
    lesson_id = Column(Integer, ForeignKey('lesson.id',ondelete="CASCADE"))

class CourseReview(BaseModel):
    id = Column(Integer, primary_key=True)
    comment = Column(Text)
    rating = Column(Integer)

    user_id = Column(Integer, ForeignKey('user.id',ondelete="CASCADE"))
    course_id = Column(Integer, ForeignKey('course.id',ondelete="CASCADE"))
