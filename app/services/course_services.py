from app.extensions import db
from app.models.course import Course,Chapter,Lesson,Category,Enrollment,CourseReview,LessonProgress,LessonHistory
from app.models.user import Teacher
from sqlalchemy import func


from sqlalchemy import or_

# def save_course_history(course, action):
#     history = CourseHistory(
#         action=action,
#         title=course.title,
#         description=course.description,
#         price=course.price,
#         image=course.image,
#         is_sequential=course.is_sequential,
#         is_public=course.is_public,
#         category_id=course.category_id,
#         course_id=course.id,
#         teacher_id=course.teacher_id,
#     )
#     db.session.add(history)
def get_my_courses(user_id):
    courses = (
        db.session.query(Course)  # ✅ dùng db.session.query thay vì db.query
        .join(Enrollment)
        .filter(Enrollment.user_id == user_id)
        .all()
    )
    return courses

def save_lesson_history(lesson, user_id, action):
    history = LessonHistory(
        action=action,
        title=lesson.title,
        description=lesson.description,
        type=lesson.type,
        content_url=lesson.content_url,
        image=lesson.image,
        is_published=lesson.is_published,
        order=lesson.order,
        is_locked=lesson.is_locked,
        lesson_id=lesson.id,
        user_id=user_id,
    )
    db.session.add(history)

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

def search_courses_by_query(query):
    search = f"%{query.lower()}%"
    return Course.query.join(Teacher, Course.teacher_id == Teacher.id) \
        .join(Category, Course.category_id == Category.id) \
        .filter(
            db.and_(
                db.or_(
                    db.func.lower(Course.title).like(search),
                    db.func.lower(Teacher.first_name).like(search),
                    db.func.lower(Teacher.last_name).like(search),
                    db.func.lower(Category.name).like(search),
                    db.func.lower(db.func.concat(Teacher.first_name, ' ', Teacher.last_name)).like(search)
                ),
                Course.is_public == True,
                Course.is_active == True
            )
        ).all()


def get_total_students_by_teacher(teacher_id):
    """Thống kê tổng số học viên theo giáo viên"""
    return db.session.query(func.count(Enrollment.user_id.distinct())) \
        .join(Course, Course.id == Enrollment.course_id) \
        .filter(Course.teacher_id == teacher_id).scalar()

def get_chapter_lesson_count_by_teacher(teacher_id):
    """Thống kê tổng số chương và bài học của giáo viên"""
    chapter_count = db.session.query(func.count(Chapter.id)) \
        .join(Course, Course.id == Chapter.course_id) \
        .filter(Course.teacher_id == teacher_id).scalar()

    lesson_count = db.session.query(func.count(Lesson.id)) \
        .join(Chapter, Chapter.id == Lesson.chapter_id) \
        .join(Course, Course.id == Chapter.course_id) \
        .filter(Course.teacher_id == teacher_id).scalar()

    return {"chapters": chapter_count, "lessons": lesson_count}


def get_avg_lessons_per_chapter(teacher_id):
    """ Thống kê trung bình số bài học mỗi chương của giáo viên"""
    subquery = db.session.query(
        Chapter.id,
        func.count(Lesson.id).label("lesson_count")
    ).join(Lesson) \
     .join(Course, Course.id == Chapter.course_id) \
     .filter(Course.teacher_id == teacher_id) \
     .group_by(Chapter.id) \
     .subquery()

    result = db.session.query(func.avg(subquery.c.lesson_count)).scalar()
    return round(result or 0, 2)

def get_published_lesson_rate(teacher_id):
    """Thống kê tỷ lệ bài học đã xuất bản / tổng bài học"""
    total = db.session.query(func.count(Lesson.id)) \
        .join(Chapter, Chapter.id == Lesson.chapter_id) \
        .join(Course, Course.id == Chapter.course_id) \
        .filter(Course.teacher_id == teacher_id).scalar()

    published = db.session.query(func.count(Lesson.id)) \
        .join(Chapter, Chapter.id == Lesson.chapter_id) \
        .join(Course, Course.id == Chapter.course_id) \
        .filter(Course.teacher_id == teacher_id, Lesson.is_published == True).scalar()

    return {"published": published, "total": total, "rate": round((published / total) * 100, 2) if total else 0}

def get_average_teacher_rating(teacher_id):
    """Thống kê trung bình đánh giá của giáo viên"""
    result = db.session.query(func.avg(CourseReview.rating)) \
        .join(Course, Course.id == CourseReview.course_id) \
        .filter(Course.teacher_id == teacher_id).scalar()
    return round(result or 0, 2)

def get_students_with_completed_lessons(teacher_id):
    """Thống kê số học viên hoàn thành ít nhất một bài học"""
    result = db.session.query(func.count(LessonProgress.user_id.distinct())) \
        .join(Lesson, Lesson.id == LessonProgress.lesson_id) \
        .join(Chapter, Chapter.id == Lesson.chapter_id) \
        .join(Course, Course.id == Chapter.course_id) \
        .filter(Course.teacher_id == teacher_id, LessonProgress.is_completed == True).scalar()
    return result

def get_enrollment_status(user_id, course_id):
    from app.models.course import Enrollment
    is_enrolled = False
    payment_status = False
    progress = 0.0
    status = None
    enrollment = Enrollment.query.filter_by(user_id=user_id, course_id=course_id).first()
    if enrollment:
        is_enrolled = True
        payment_status = enrollment.payment_status
        progress = enrollment.progress
        status = enrollment.status.value if enrollment.status else None
    return {
        'is_enrolled': is_enrolled,
        'payment_status': payment_status,
        'progress': progress,
        'status': status
    }


