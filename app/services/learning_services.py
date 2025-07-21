from app.models.course import Lesson, Chapter, Course, LessonProgress, Enrollment, Status
from app.extensions import db

def get_lesson_by_id(lesson_id):
    return Lesson.query.filter_by(id=lesson_id).first()

def get_prev_lesson(course_id, chapter_order, lesson_order):
    # Nếu không phải bài đầu tiên của chương
    if lesson_order > 1:
        return Lesson.query.filter_by(
            chapter_id=Chapter.query.filter_by(course_id=course_id, order=chapter_order).first().id,
            order=lesson_order-1
        ).first()
    # Nếu là bài đầu tiên của chương (lesson_order == 1)
    else:
        prev_chapter = Chapter.query.filter_by(course_id=course_id, order=chapter_order-1).first()
        if not prev_chapter:
            return None
        return Lesson.query.filter_by(chapter_id=prev_chapter.id).order_by(Lesson.order.desc()).first()

def get_enrollment(user_id, course_id):
    return Enrollment.query.filter_by(user_id=user_id, course_id=course_id).first()

def get_lesson_progress(user_id, lesson_id):
    return LessonProgress.query.filter_by(user_id=user_id, lesson_id=lesson_id).first()

def get_next_lesson(chapter_id, order):
    return Lesson.query.filter_by(chapter_id=chapter_id, order=order+1).first()

def get_total_and_completed_lessons(user_id, course):
    total_lessons = sum(len(chapter.lessons) for chapter in course.chapters)
    completed_lessons = LessonProgress.query.filter_by(
        user_id=user_id, is_completed=True
    ).join(Lesson).join(Chapter).filter(Chapter.course_id == course.id).count()
    return total_lessons, completed_lessons

def add_lesson_progress(lesson_progress):
    db.session.add(lesson_progress)
    db.session.commit()

def commit():
    db.session.commit()

def get_course_progress(course_id, user_id):
    try:
        # Lấy enrollment
        enrollment = get_enrollment(user_id, course_id)
        if not enrollment:
            return None, "Bạn chưa đăng ký khóa học này"
        
        # Lấy course
        course = Course.query.get(course_id)
        if not course:
            return None, "Không tìm thấy khóa học"
        
        # Lấy tất cả lesson progress của user trong course này
        lesson_progresses = db.session.query(LessonProgress).join(Lesson).join(Chapter).filter(
            LessonProgress.user_id == user_id,
            Chapter.course_id == course_id
        ).all()
        
        return {
            "enrollment": enrollment,
            "course": course,
            "lesson_progresses": lesson_progresses
        }, None
        
    except Exception as e:
        return None, str(e)

