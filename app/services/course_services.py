from app.extensions import db
from app.models.course import Course,Chapter,Lesson,Category,Enrollment
from app.models.user import Teacher

from sqlalchemy import or_

# from flask_sqlalchemy import Pagination
def get_courses(page, per_page):
    return Course.query.order_by(Course.created_day.desc()).paginate(page=page, per_page=per_page, error_out=False)

    # return Course.query.filter_by(is_public = True).all()
def get_courses_by_teacher_id_not_public(teacher_id, page, per_page):
    return Course.query.filter_by(teacher_id=teacher_id, is_public=False).order_by(Course.created_day.desc()).paginate(page=page, per_page=per_page, error_out=False)

    # return Course.query.filter(
    #     Course.is_public == False,
    #     Course.teacher_id == id
    # ).all()
def get_courses_by_teacher_id_public(teacher_id, page, per_page):
    return Course.query.filter_by(teacher_id=teacher_id, is_public=True).order_by(Course.created_day.desc()).paginate(page=page, per_page=per_page, error_out=False)

    # return Course.query.filter(
    #     Course.is_public == True,
    #     Course.teacher_id == id
    # ).all()


def get_course_by_id(id):
    return Course.query.filter_by(id=id).first()

def get_chapter_by_id(id):
    return Chapter.query.filter_by(id=id).first()
def get_chapter_by_course_id(id):
    return Chapter.query.filter_by(course_id=id).all()

def get_category_by_id(id):
    return Category.query.filter_by(id=id).first()
def get_categories():
    return Category.query.all()

def create_course_in_db(**kwargs):
    course = Course(**kwargs)
    db.session.add(course)
    db.session.commit()
    return course

def create_chapter_in_db(**kwargs):
    chater = Chapter(
        title=kwargs["title"],
        description=kwargs["description"],
        course_id=kwargs["course_id"],
        order=kwargs["order"],
    )
    db.session.add(chater)
    db.session.commit()
    return chater
def create_lesson_in_db(**kwargs):
    lesson = Lesson(**kwargs)
    db.session.add(lesson)
    db.session.commit()
    return lesson

def get_lesson_by_id(id):
    return Lesson.query.filter_by(id=id).first()

def get_courses_by_teacher(teacher_id):
    """Lấy danh sách khóa học của một giáo viên"""
    return Course.query.filter_by(teacher_id=teacher_id, is_active=True).all()

def get_courses_by_category(category_id):
    """Lấy danh sách khóa học theo danh mục"""
    return Course.query.filter_by(category_id=category_id, is_public=True, is_active=True).all()

def get_courses_by_student(student_id):
    """Lấy danh sách khóa học mà học viên đã đăng ký"""
    # Lấy các khóa học thông qua bảng enrollment
    enrollments = Enrollment.query.filter_by(user_id=student_id).all()
    course_ids = [enrollment.course_id for enrollment in enrollments]

    if not course_ids:
        return []

    return Course.query.filter(Course.id.in_(course_ids), Course.is_active == True).all()

def search_courses(query):
    """Tìm kiếm khóa học theo từ khóa trong title và description"""
    # Tìm kiếm trong title và description
    return Course.query.filter(
        or_(
            Course.title.ilike(f'%{query}%'),
            Course.description.ilike(f'%{query}%')
        ),
        Course.is_public == True,
        Course.is_active == True
    ).all()