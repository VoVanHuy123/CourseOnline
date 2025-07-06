from flask import Blueprint, jsonify, request
from flask_apispec import use_kwargs, marshal_with, doc
from app.schemas.course import CourseSchema
from app.extensions import login_manager
from app.services.course_services import get_courses
from app.perms.perms import teacher_required

course_bp = Blueprint("course",__name__,url_prefix="/courses")

@course_bp.route("/", methods=["GET"])
@doc(description="Khóa học", tags=["Course"])
@marshal_with(CourseSchema(many=True), code=200)  
@teacher_required
def list_courses():
    courses = get_courses()
    return courses

#

@course_bp.route("/", methods=['POST'])
@doc(description="Tạo khóa học mới", tags=["Course"])
@use_kwargs(CourseSchema, location="json")  # Input schema
@marshal_with(CourseSchema)  # Output schema
@teacher_required
def create_course(**kwargs):
    # Ở đây bạn có thể tạo khóa học mới với kwargs chứa dữ liệu từ client
    # new_course = create_course_service(kwargs)  # hoặc db.session.add(...)
    # return new_course
    pass


# thêm vào swagger-ui
#đăng kí các hàm ở đây để hiện lên swagger
def course_register_docs(docs):
    docs.register(list_courses, blueprint='course')
    docs.register(create_course, blueprint='course')