from flask import Blueprint, jsonify, request
from flask_apispec import use_kwargs, marshal_with, doc
from app.schemas.course import CourseSchema,ChapterSchema,LessonSchema,CourseCreateResponseSchema,ChapterCreateResponseSchema,LessonCreateResponseSchema
from app.extensions import login_manager
from app.services import course_services ,services
from app.services.user_services import get_teacher
from app.perms.perms import teacher_required
from flask_jwt_extended import  get_jwt_identity
from app.extensions import db
import traceback
import cloudinary.uploader

course_bp = Blueprint("course",__name__,url_prefix="/courses")

@course_bp.route("/", methods=["GET"],provide_automatic_options=False)
@doc(description="Khóa học", tags=["Course"])
@marshal_with(CourseSchema(many=True), code=200)  
def list_courses():
    courses = course_services.get_courses()
    return courses

@course_bp.route("/<int:course_id>", methods=["GET"])
@doc(description="Lấy chi tiết khóa học theo ID", tags=["Course"])
@marshal_with(CourseSchema, code=200)
def get_course_detail(course_id):
    """API lấy chi tiết khóa học theo ID"""
    course = course_services.get_course_by_id(course_id)
    if not course:
        return {"message": "Khóa học không tồn tại"}, 404
    return course

@course_bp.route("/teacher/<int:teacher_id>", methods=["GET"])
@doc(description="Lấy danh sách khóa học theo giáo viên", tags=["Course"])
@marshal_with(CourseSchema(many=True), code=200)
def get_courses_by_teacher(teacher_id):
    """API lấy danh sách khóa học của một giáo viên"""
    courses = course_services.get_courses_by_teacher(teacher_id)
    return courses

@course_bp.route("/category/<int:category_id>", methods=["GET"])
@doc(description="Lấy danh sách khóa học theo danh mục", tags=["Course"])
@marshal_with(CourseSchema(many=True), code=200)
def get_courses_by_category(category_id):
    """API lấy danh sách khóa học theo danh mục"""
    courses = course_services.get_courses_by_category(category_id)
    return courses

@course_bp.route("/student/<int:student_id>", methods=["GET"])
@doc(description="Lấy danh sách khóa học đã đăng ký của học viên", tags=["Course"])
@marshal_with(CourseSchema(many=True), code=200)
def get_courses_by_student(student_id):
    """API lấy danh sách khóa học mà học viên đã đăng ký"""
    courses = course_services.get_courses_by_student(student_id)
    return courses

@course_bp.route("/search", methods=["GET"])
@doc(description="Tìm kiếm khóa học theo từ khóa", tags=["Course"])
@marshal_with(CourseSchema(many=True), code=200)
def search_courses():
    """API tìm kiếm khóa học theo từ khóa trong title và description"""
    # Lấy tham số query từ URL
    query = request.args.get('q', '').strip()

    if not query:
        return {"message": "Vui lòng nhập từ khóa tìm kiếm"}, 400

    courses = course_services.search_courses(query)
    return courses

#

@course_bp.route("/", methods=['POST'],provide_automatic_options=False)
@doc(description="Tạo khóa học mới", tags=["Course"])
@use_kwargs(CourseSchema, location="json")  # Input schema
@marshal_with(CourseCreateResponseSchema, code=201) 
@teacher_required
def create_course(**kwargs):
    # Lấy user hiện tại từ JWT (giả định bạn dùng Flask-JWT-Extended)
    teacher_id = get_jwt_identity()
    image_path = request.files.get("image")
    image = None

    # Lấy teacher gắn với user (nếu dùng quan hệ 1-1 giữa User và Teacher)
    teacher = get_teacher(teacher_id)
    if not teacher:
        return {"msg": "Không tìm thấy giáo viên tương ứng với người dùng"}, 404
    
    if image_path:
        result = cloudinary.uploader.upload(image_path)
        image = result['secure_url']
    

    kwargs["teacher_id"]=teacher_id
    kwargs["image"] = image

    # Tạo đối tượng Course mới từ kwargs (đã validate qua CourseSchema)
    try:
        course = course_services.create_course_in_db(**kwargs)
        return {"msg": "Tạo khoá học thành công", "course_title": course.title}, 201
    except Exception as e:
        traceback.print_exc()
        return {"msg": "Lỗi hệ thống", "error": str(e)}, 500


@course_bp.route("/<int:course_id>", methods=["PATCH"],provide_automatic_options=False)
@doc(description="Cập nhật khóa học", tags=["Course"])
@teacher_required
def update_course(course_id):
    try:
        course = course_services.get_course_by_id(course_id)
        if not course:
            return {"msg": "Không tìm thấy khoá học"}, 404

        data = request.form  # Nếu có file thì dùng form-data
        image_file = request.files.get("image")

        if "title" in data:
            course.title = data["title"]
        if "description" in data:
            course.description = data["description"]
        if "price" in data:
            course.price = data["price"]
        if "category_id" in data:
            course.category_id = data["category_id"]
        if image_file:
            result = cloudinary.uploader.upload(image_file)
            course.image = result["secure_url"]

        db.session.commit()
        return {"msg": "Cập nhật khoá học thành công"}, 200
    except Exception as e:
        traceback.print_exc()
        return {"msg": "Lỗi hệ thống", "error": str(e)}, 500



@course_bp.route("/<int:course_id>", methods=["DELETE"],provide_automatic_options=False)
@doc(description="Xóa khoá học", tags=["Course"])
@teacher_required
def delete_course(course_id):
    try:
        course = course_services.get_course_by_id(course_id)
        if not course:
            return {"msg": "Không tìm thấy khoá học"}, 404

        db.session.delete(course)
        db.session.commit()
        return {"msg": f"Đã xoá khoá học '{course.title}'"}, 200
    except Exception as e:
        traceback.print_exc()
        return {"msg": "Lỗi hệ thống", "error": str(e)}, 500


@course_bp.route("/chapters",methods = ['POST'],provide_automatic_options=False)
@doc(description="Tạo Chương mới",tags = ["Course"])
@use_kwargs(ChapterSchema, location="json")
@marshal_with(ChapterCreateResponseSchema,201)
@teacher_required
def create_chapter(**kwargs):
    course_id = kwargs.get("course_id")
    course = course_services.get_course_by_id(course_id)
    if not course:
        return {"msg":"Không tìm thấy khóa học"}
    try:
        chapter = course_services.create_chapter_in_db(**kwargs)
        return {"msg": "Tạo chương thành công", "chapter_title": chapter.title}, 201
    except Exception as e:
        traceback.print_exc()
        return {"msg": "Lỗi hệ thống", "error": str(e)}, 500
    
@course_bp.route("/chapter/<int:chapter_id>", methods=["PATCH"],provide_automatic_options=False)
@doc(description="Cập nhật chương học", tags=["Course"])
@teacher_required
def update_chapter(chapter_id):
    try:
        chapter = course_services.get_chapter_by_id(chapter_id)
        if not chapter:
            return {"msg": "Không tìm thấy chương"}, 404

        data = request.get_json()

        if "title" in data:
            chapter.title = data["title"]
        if "description" in data:
            chapter.description = data["description"]
        if "course_id" in data:
            chapter.course_id = data["course_id"]

        db.session.commit()
        return {"msg": "Cập nhật chương thành công"}, 200
    except Exception as e:
        traceback.print_exc()
        return {"msg": "Lỗi hệ thống", "error": str(e)}, 500

@course_bp.route("/chapter/<int:chapter_id>", methods=["DELETE"],provide_automatic_options=False)
@doc(description="Xóa chương học", tags=["Course"])
@teacher_required
def delete_chapter(chapter_id):
    try:
        chapter = course_services.get_chapter_by_id(chapter_id)
        if not chapter:
            return {"msg": "Không tìm thấy chương"}, 404

        db.session.delete(chapter)
        db.session.commit()
        return {"msg": f"Đã xoá chương '{chapter.title}'"}, 200
    except Exception as e:
        traceback.print_exc()
        return {"msg": "Lỗi hệ thống", "error": str(e)}, 500

    

@course_bp.route("/lessons", methods=['POST'],provide_automatic_options=False)
@doc(description="Tạo bài học mới có video", tags=["Course"],provide_automatic_options=False)
@use_kwargs(LessonSchema, location="json")
@marshal_with(LessonCreateResponseSchema,201)
@teacher_required
def create_lesson(**kwargs):
    try:
        is_locked = False
        content_url = None
        chapter_id = kwargs["chapter_id"]
        lesson_type=kwargs["type"]

        chapter  = course_services.get_chapter_by_id(chapter_id)
        if not chapter:
            return {"msg": "Không tìm thấy chương"}, 404

        # Lấy course của chapter và kiểm tra is_sequential
        course = course_services.get_course_by_id(chapter.course_id)
        if course and course.is_sequential:
            is_locked = True  

        file = request.files.get("content_url")
        if file:
            if(lesson_type == "video"):

                result = cloudinary.uploader.upload(
                    file,
                    resource_type="video"  
                )
                content_url = result['secure_url']
            elif(lesson_type=="file") :
                result = cloudinary.uploader.upload(
                    file,
                    resource_type="raw" 
                )
                content_url = result['secure_url']
        kwargs["content_url"] = content_url
        kwargs["is_locked"] = is_locked
        
        lesson = course_services.create_lesson_in_db(**kwargs)

        return {"msg": "Tạo bài học thành công","lesson_title":lesson.title, "lesson_id": lesson.id}, 201

    except Exception as e:
        traceback.print_exc()
        return {"msg": "Lỗi hệ thống", "error": str(e)}, 500
    
@course_bp.route("/lesson/<int:lesson_id>", methods=["PATCH"],provide_automatic_options=False)
@doc(description="Cập nhật bài học", tags=["Course"])
@teacher_required
def update_lesson(lesson_id):
    try:
        lesson = course_services.get_lesson_by_id(lesson_id)
        if not lesson:
            return {"msg": "Không tìm thấy bài học"}, 404

        data = request.form
        file = request.files.get("content_url")

        if "title" in data:
            lesson.title = data["title"]
        if "description" in data:
            lesson.description = data["description"]
        if "type" in data:
            lesson.type = data["type"]
        if "chapter_id" in data:
            lesson.chapter_id = data["chapter_id"]
        if "order" in data:
            lesson.order = data["order"]
        if "is_published" in data:
            lesson.is_published = data["is_published"] == "true"
        if "is_locked" in data:
            lesson.is_locked = data["is_locked"] == "true"

        if file:
            # Upload lại nếu có file mới
            resource_type = "video" if lesson.type == "video" else "raw"
            result = cloudinary.uploader.upload(file, resource_type=resource_type)
            lesson.content_url = result["secure_url"]

        db.session.commit()
        return {"msg": "Cập nhật bài học thành công"}, 200
    except Exception as e:
        traceback.print_exc()
        return {"msg": "Lỗi hệ thống", "error": str(e)}, 500


@course_bp.route("/lesson/<int:lesson_id>", methods=["DELETE"],provide_automatic_options=False)
@doc(description="Xóa bài học", tags=["Course"])
@teacher_required
def delete_lesson(lesson_id):
    try:
        lesson = course_services.get_lesson_by_id(lesson_id)
        if not lesson:
            return {"msg": "Không tìm thấy bài học"}, 404

        db.session.delete(lesson)
        db.session.commit()
        return {"msg": f"Đã xoá bài học '{lesson.title}'"}, 200
    except Exception as e:
        traceback.print_exc()
        return {"msg": "Lỗi hệ thống", "error": str(e)}, 500

# thêm vào swagger-ui
#đăng kí các hàm ở đây để hiện lên swagger
def course_register_docs(docs):
    docs.register(list_courses, blueprint='course')
    docs.register(get_course_detail, blueprint='course')
    docs.register(get_courses_by_teacher, blueprint='course')
    docs.register(get_courses_by_category, blueprint='course')
    docs.register(get_courses_by_student, blueprint='course')
    docs.register(search_courses, blueprint='course')
    docs.register(create_course, blueprint='course')
    docs.register(create_chapter, blueprint='course')
    docs.register(create_lesson, blueprint='course')
    docs.register(update_course, blueprint='course')
    docs.register(update_chapter, blueprint='course')
    docs.register(update_lesson, blueprint='course')
    docs.register(delete_course, blueprint='course')
    docs.register(delete_chapter, blueprint='course')
    docs.register(delete_lesson, blueprint='course')
