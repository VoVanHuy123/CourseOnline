from flask import Blueprint
from flask_apispec import doc
from app.services import stats_services
from app.perms.perms import teacher_required
from flask_jwt_extended import get_jwt_identity
import traceback

stats_bp = Blueprint("stats", __name__, url_prefix="/stats")

@stats_bp.route("/total-students", methods=["GET"])
@doc(description="Thống kê tổng số học viên của giáo viên", tags=["Stats"])
@teacher_required
def get_total_students():
    try:
        teacher_id = get_jwt_identity()
        total = stats_services.get_total_students_by_teacher(teacher_id)
        return {"msg": "Thống kê học viên thành công", "total_students": total}, 200
    except Exception as e:
        traceback.print_exc()
        return {"msg": "Lỗi hệ thống", "error": str(e)}, 500

@stats_bp.route("/chapters-lessons", methods=["GET"])
@doc(description="Thống kê tổng số chương và bài học", tags=["Stats"])
@teacher_required
def get_chapter_lesson_counts():
    try:
        teacher_id = get_jwt_identity()
        result = stats_services.get_chapter_lesson_count_by_teacher(teacher_id)
        return {"msg": "Thống kê thành công", "data": result}, 200
    except Exception as e:
        return {"msg": "Lỗi hệ thống", "error": str(e)}, 500

@stats_bp.route("/avg-lessons-per-chapter", methods=["GET"])
@doc(description="Thống kê trung bình số bài học mỗi chương", tags=["Stats"])
@teacher_required
def get_avg_lessons():
    try:
        teacher_id = get_jwt_identity()
        avg = stats_services.get_avg_lessons_per_chapter(teacher_id)
        return {"msg": "Thống kê thành công", "average_lessons": avg}, 200
    except Exception as e:
        return {"msg": "Lỗi hệ thống", "error": str(e)}, 500

@stats_bp.route("/published-lesson-rate", methods=["GET"])
@doc(description="Thống kê tỷ lệ bài học đã xuất bản", tags=["Stats"])
@teacher_required
def get_publish_rate():
    try:
        teacher_id = get_jwt_identity()
        data = stats_services.get_published_lesson_rate(teacher_id)
        return {"msg": "Thống kê thành công", "data": data}, 200
    except Exception as e:
        return {"msg": "Lỗi hệ thống", "error": str(e)}, 500

@stats_bp.route("/avg-rating", methods=["GET"])
@doc(description="Thống kê trung bình đánh giá của giáo viên", tags=["Stats"])
@teacher_required
def get_avg_rating():
    try:
        teacher_id = get_jwt_identity()
        avg_rating = stats_services.get_average_teacher_rating(teacher_id)
        return {"msg": "Thống kê thành công", "avg_rating": avg_rating}, 200
    except Exception as e:
        return {"msg": "Lỗi hệ thống", "error": str(e)}, 500

@stats_bp.route("/students-completed-lessons", methods=["GET"])
@doc(description="Thống kê số học viên đã hoàn thành ít nhất một bài học", tags=["Stats"])
@teacher_required
def get_students_completed_lessons():
    try:
        teacher_id = get_jwt_identity()
        total = stats_services.get_students_with_completed_lessons(teacher_id)
        return {"msg": "Thống kê thành công", "students_completed": total}, 200
    except Exception as e:
        return {"msg": "Lỗi hệ thống", "error": str(e)}, 500

# Đăng ký các route để hiển thị lên Swagger
def stats_register_docs(docs):
    docs.register(get_total_students, blueprint='stats')
    docs.register(get_chapter_lesson_counts, blueprint='stats')
    docs.register(get_avg_lessons, blueprint='stats')
    docs.register(get_publish_rate, blueprint='stats')
    docs.register(get_avg_rating, blueprint='stats')
    docs.register(get_students_completed_lessons, blueprint='stats')





