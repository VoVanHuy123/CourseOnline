from app.extensions import db
from app.models.course import Course, Chapter, Lesson, Enrollment, CourseReview, LessonProgress
from sqlalchemy import func

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
    """Thống kê trung bình số bài học mỗi chương của giáo viên"""
    subquery = db.session.query(
        Chapter.id,
        func.count(Lesson.id).label("lesson_count")
    ).join(Lesson) \
     .join(Course, Course.id == Chapter.course_id) \
     .filter(Course.teacher_id == teacher_id) \
     .group_by(Chapter.id) \
     .subquery()

    result = db.session.query(func.avg(subquery.c.lesson_count)).scalar()
    return round(result or 0)

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

    return {
        "published": published, 
        "total": total, 
        "rate": round((published / total) * 100, 2) if total else 0
    }

def get_average_teacher_rating(teacher_id):
    """Thống kê trung bình đánh giá của giáo viên"""
    result = db.session.query(func.avg(CourseReview.rating)) \
        .join(Course, Course.id == CourseReview.course_id) \
        .filter(Course.teacher_id == teacher_id).scalar()
    return round(result or 0, 1)

def get_students_with_completed_lessons(teacher_id):
    """Thống kê số học viên hoàn thành ít nhất một bài học"""
    result = db.session.query(func.count(LessonProgress.user_id.distinct())) \
        .join(Lesson, Lesson.id == LessonProgress.lesson_id) \
        .join(Chapter, Chapter.id == Lesson.chapter_id) \
        .join(Course, Course.id == Chapter.course_id) \
        .filter(Course.teacher_id == teacher_id, LessonProgress.is_completed == True).scalar()
    return result
