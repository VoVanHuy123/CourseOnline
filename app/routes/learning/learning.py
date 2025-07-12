from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity
from app.perms.perms import student_required
from app.services import learning_services
from app.models.course import LessonProgress, Status
import traceback
from flask_apispec import doc, marshal_with
from app.schemas.course import LessonProgressSchema, EnrollmentSchema

learning_bp = Blueprint("learning", __name__, url_prefix="/learning")

@learning_bp.route("/lessons/<int:lesson_id>/complete", methods=["POST"])
@doc(description="Hoàn thành bài học", tags=["Learning"])
@student_required
def complete_lesson(lesson_id):
    try:
        user_id = get_jwt_identity()
        lesson = learning_services.get_lesson_by_id(lesson_id)
        if not lesson:
            return {"msg": "Không tìm thấy bài học"}, 404

        enrollment = learning_services.get_enrollment(user_id, lesson.chapter.course_id)
        if not enrollment:
            return {"msg": "Bạn chưa đăng ký khóa học này"}, 403

        prev_lesson = learning_services.get_prev_lesson(lesson.chapter.course_id, lesson.chapter.order, lesson.order)
        if prev_lesson:
            prev_progress = learning_services.get_lesson_progress(user_id, prev_lesson.id)
            if not prev_progress or not prev_progress.is_completed:
                return {"msg": "Bạn phải hoàn thành bài học trước đó"}, 403

        lesson_progress = learning_services.get_lesson_progress(user_id, lesson_id)
        if not lesson_progress:
            lesson_progress = LessonProgress(
                user_id=user_id,
                lesson_id=lesson_id,
                is_completed=True
            )
            learning_services.add_lesson_progress(lesson_progress)
        else:
            lesson_progress.is_completed = True
            learning_services.commit()

        course = lesson.chapter.course
        total_lessons, completed_lessons = learning_services.get_total_and_completed_lessons(user_id, course)
        enrollment.progress = (completed_lessons / total_lessons) * 100 if total_lessons > 0 else 0
        enrollment.status = Status.COMPLETED.value if enrollment.progress >= 100 else Status.UNFINISHED.value
        learning_services.commit()

        return {
            "msg": "Đánh dấu hoàn thành bài học thành công",
            "lesson_id": lesson_id,
            "course_progress": enrollment.progress,
            "status": enrollment.status
        }, 200
    except Exception as e:
        traceback.print_exc()
        return {"msg": "Lỗi hệ thống", "error": str(e)}, 500

@learning_bp.route("/lessons/<int:lesson_id>/uncomplete", methods=["POST"])
@doc(description="Bỏ hoàn thành bài học", tags=["Learning"])
@marshal_with(LessonProgressSchema, code=200)
@student_required
def uncomplete_lesson(lesson_id):
    try:
        user_id = get_jwt_identity()
        data, err = learning_services.uncomplete_lesson(lesson_id, user_id)
        if not data:
            return {"msg": err}, 404
        return data, 200
    except Exception as e:
        traceback.print_exc()
        return {"msg": "Lỗi hệ thống", "error": str(e)}, 500

@learning_bp.route("/courses/<int:course_id>/progress", methods=["GET"])
@doc(description="Lấy tiến trình học khóa học", tags=["Learning"])
@marshal_with(EnrollmentSchema, code=200)
@student_required
def get_course_progress(course_id):
    try:
        user_id = get_jwt_identity()
        data, err = learning_services.get_course_progress(course_id, user_id)
        if not data:
            return {"msg": err}, 404
        return data, 200
    except Exception as e:
        traceback.print_exc()
        return {"msg": "Lỗi hệ thống", "error": str(e)}, 500

    
def learning_register_docs(docs):
    docs.register(complete_lesson, blueprint='learning')
    docs.register(uncomplete_lesson, blueprint='learning')
    docs.register(get_course_progress, blueprint='learning')

# note