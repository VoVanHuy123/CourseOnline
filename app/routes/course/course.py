from flask import Blueprint, jsonify, request
from flask_apispec import use_kwargs, marshal_with, doc
from app.schemas.course import CourseSchema,ChapterSchema,LessonSchema,CourseCreateResponseSchema,ChapterCreateResponseSchema,LessonInChapterDumpSchema,CategorySchema,ListChapterSchema,EnrollmentResponseSchema,EnrollmentRequestSchema,EnrollmentSchema
from app.extensions import login_manager
from app.services import course_services ,services
from app.services.user_services import get_teacher
from app.services import enrollment_services, payment_services
from app.perms.perms import teacher_required,login_required,student_required,owner_required
from app.models.course import Type,Course
from flask_jwt_extended import  get_jwt_identity
# from flask_sqlalchemy import Pagination
from marshmallow import fields
from app.extensions import db
import traceback,os
import cloudinary.uploader
# from flask_jwt_extended import jwt_required
course_bp = Blueprint("course",__name__,url_prefix="/courses")

@course_bp.route("/", methods=["GET"])
@doc(description="Khóa học của tất cả giáo viên", tags=["Course"])
@use_kwargs({
    "page": fields.Int(missing=1),
    "per_page": fields.Int(missing=10)
}, location="query")
def list_courses(page, per_page):
    pagination = course_services.get_courses(page, per_page)
    return {
        "data": CourseSchema(many=True).dump(pagination.items),
        "page": pagination.page,
        "per_page": pagination.per_page,
        "total_items": pagination.total,
        "total_pages": pagination.pages
    }
@course_bp.route("/teacher/<int:teacher_id>/not-public", methods=["GET"])
@doc(description="Khóa học của giáo viên chưa đăng tải", tags=["Course"])
@teacher_required
@use_kwargs({
    "page": fields.Int(missing=1),
    "per_page": fields.Int(missing=10)
}, location="query")
def list_teacher_courses_not_public(teacher_id, page, per_page):
    pagination = course_services.get_courses_by_teacher_id_not_public(teacher_id, page, per_page)
    return {
        "data": CourseSchema(many=True).dump(pagination.items),
        "page": pagination.page,
        "per_page": pagination.per_page,
        "total_items": pagination.total,
        "total_pages": pagination.pages
    }
@course_bp.route("/teacher/<int:teacher_id>/public", methods=["GET"])
@doc(description="Khóa học của giáo viên đã đăng tải", tags=["Course"])
@teacher_required
@use_kwargs({
    "page": fields.Int(missing=1),
    "per_page": fields.Int(missing=10)
}, location="query")
def list_teacher_courses_public(teacher_id, page, per_page):
    pagination = course_services.get_courses_by_teacher_id_public(teacher_id, page, per_page)
    return {
        "data": CourseSchema(many=True).dump(pagination.items),
        "page": pagination.page,
        "per_page": pagination.per_page,
        "total_items": pagination.total,
        "total_pages": pagination.pages
    }

@course_bp.route("/<int:course_id>", methods=["GET"], provide_automatic_options=False)
@doc(description="Lấy chi tiết khóa học theo ID", tags=["Course"])
def get_course_detail(course_id):
    """API lấy chi tiết khóa học theo ID với thông tin enrollment status"""
    course = course_services.get_course_by_id(course_id)
    if not course:
        return {"message": "Khóa học không tồn tại"}, 404

    # Serialize course data
    course_data = CourseSchema().dump(course)

    # Thêm thông tin enrollment status nếu user đã đăng nhập
    try:
        from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
        verify_jwt_in_request(optional=True)
        user_id = get_jwt_identity()

        if user_id:
            enrollment = enrollment_services.get_enrollment_by_user_and_course(user_id, course_id)
            if enrollment:
                course_data['enrollment_status'] = {
                    'is_enrolled': True,
                    'payment_status': enrollment.payment_status,
                    'progress': enrollment.progress,
                    'status': enrollment.status.value if enrollment.status else 'unfinished'
                }
            else:
                course_data['enrollment_status'] = {
                    'is_enrolled': False,
                    'payment_status': False,
                    'progress': 0.0,
                    'status': None
                }
        else:
            course_data['enrollment_status'] = {
                'is_enrolled': False,
                'payment_status': False,
                'progress': 0.0,
                'status': None
            }
    except Exception as e:
        course_data['enrollment_status'] = {
            'is_enrolled': False,
            'payment_status': False,
            'progress': 0.0,
            'status': None
        }

    return course_data, 200

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

@course_bp.route("", methods=['POST'])
@doc(description="Tạo khóa học mới", tags=["Course"])
@use_kwargs(CourseSchema, location="form")  # Input schema
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


@course_bp.route("/<int:course_id>", methods=["PATCH"])
@doc(description="Cập nhật khóa học", tags=["Course"])
@teacher_required
@owner_required(model=Course,lookup_arg="course_id",user_field="teacher_id")
def update_course(course_id):
    try:
        course = course_services.get_course_by_id(course_id)
        if not course:
            return {"msg": "Không tìm thấy khoá học"}, 404

        data = request.form  # Nếu có file thì dùng form-data
        image_file = request.files.get("image")
        print("vaof")
        if "title" in data:
            course.title = data["title"]
        if "description" in data:
            course.description = data["description"]
        if "price" in data:
            course.price = float(data["price"])
        if "category_id" in data:
            course.category_id = int(data["category_id"])
        if "is_sequential" in data:
            course.is_sequential = data["is_sequential"].lower() == "true"
        if "is_public" in data:
            course.is_public = data["is_public"].lower() == "true"
        if "null_image" in data:
            course.image = data["null_image"]
        
        if image_file:
            result = cloudinary.uploader.upload(image_file)
            course.image = result["secure_url"]

        db.session.commit()
        return {"msg": "Cập nhật khoá học thành công"}, 200
    except Exception as e:
        traceback.print_exc()
        return {"msg": "Lỗi hệ thống", "error": str(e)}, 500



@course_bp.route("/<int:course_id>", methods=["DELETE"])
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


@course_bp.route("/<int:course_id>/chapters",methods = ['GET'])
@doc(description="Lấy danh sách chương của khóa học",tags = ["Course"])
# @use_kwargs(ChapterSchema(many=True), location="json")
@marshal_with(ListChapterSchema(many=True),200)
def get_course_chapters(course_id):
    # course_id = kwargs.get("course_id")
    # chapters = course_services.get_chapter_by_course_id(course_id)
    # if not chapters:
    #     return {"msg":"Không tìm thấy khóa học"}
    try:
        chapters = course_services.get_chapter_by_course_id(course_id)
        return chapters
    except Exception as e:
        traceback.print_exc()
        return {"msg": "Lỗi hệ thống", "error": str(e)}, 500

@course_bp.route("/chapters",methods = ['POST'])
@doc(description="Tạo Chương mới",tags = ["Course"])
@use_kwargs(ChapterSchema, location="json")
@marshal_with(ChapterSchema(),201)
@teacher_required
def create_chapter(**kwargs):
    course_id = kwargs.get("course_id")
    course = course_services.get_course_by_id(course_id)
    if not course:
        return {"msg":"Không tìm thấy khóa học"}
    try:
        chapter = course_services.create_chapter_in_db(**kwargs)
        return chapter, 201
    except Exception as e:
        traceback.print_exc()
        return {"msg": "Lỗi hệ thống", "error": str(e)}, 500
    
@course_bp.route("/chapters/<int:chapter_id>", methods=["PATCH"])
@doc(description="Cập nhật chương học", tags=["Course"])
# @use_kwargs(ChapterSchema,location="json")
# @marshal_with(ChapterSchema,200)
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
        if "order" in data:
            chapter.order = data["order"]

        db.session.commit()
        return {"msg": "Cập nhật chương thành công"}, 200
    except Exception as e:
        traceback.print_exc()
        return {"msg": "Lỗi hệ thống", "error": str(e)}, 500

@course_bp.route("/chapter/<int:chapter_id>", methods=["DELETE"])
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

    



ALLOWED_FILE_EXT   = {"pdf", "doc", "docx", "xlsx", "ppt", "pptx", "zip"}
ALLOWED_VIDEO_EXT  = {"mp4", "mov", "avi", "mkv"}
ALLOWED_IMAGE_EXT = {"jpg", "jpeg", "png", "gif", "webp"}

def _get_extension(filename: str) -> str:
    return os.path.splitext(filename)[1][1:].lower()
@course_bp.route("/lessons", methods=['POST'])
@doc(description="Tạo bài học mới có video", tags=["Course"])
@use_kwargs(LessonSchema, location="form")
@marshal_with(LessonInChapterDumpSchema,201)
@teacher_required
def create_lesson(**kwargs):
    try:
        chapter_id  = kwargs["chapter_id"]
        lesson_type = kwargs["type"]

        chapter = course_services.get_chapter_by_id(chapter_id)
        if not chapter:
            return {"msg": "Không tìm thấy chương"}, 404

        # --- Khóa nếu course is_sequential ---
        course = course_services.get_course_by_id(chapter.course_id)
        kwargs["is_locked"] = bool(course and course.is_sequential)

        # --- Xử lý file upload ---
        upload_file = request.files.get("file")  # key='file' trong form-data
        content_url = None

        if upload_file:
            ext = _get_extension(upload_file.filename)

            if lesson_type == Type.VIDEO.value:
                if ext not in ALLOWED_VIDEO_EXT:
                    return {"msg": "Định dạng video không hỗ trợ"}, 400
                result = cloudinary.uploader.upload(
                    upload_file,
                    resource_type="video",
                    folder="lessons/videos"
                )
            elif lesson_type == Type.FILE.value:
                if ext not in ALLOWED_FILE_EXT:
                    return {"msg": "Định dạng tệp không hỗ trợ"}, 400
                result = cloudinary.uploader.upload(
                    upload_file,
                    resource_type="raw",
                    folder="lessons/files"
                )
            elif lesson_type == Type.IMAGE.value:
                if ext not in ALLOWED_IMAGE_EXT:
                    return {"msg": "Định dạng ảnh không hỗ trợ"}, 400
                result = cloudinary.uploader.upload(
                    upload_file,
                    resource_type="image",
                    folder="lessons/images"
                )
            else:
                return {"msg": "Loại bài học không yêu cầu file"}, 400

            content_url = result["secure_url"]

        kwargs["content_url"] = content_url

        # --- Lưu DB ---
        lesson = course_services.create_lesson_in_db(**kwargs)

        # return {
        #     "msg"      : "Tạo bài học thành công",
        #     "lesson_id": lesson.id,
        #     "lesson_title": lesson.title,
        #     "content_url": lesson.content_url,
        # }, 201
        return lesson, 201

    except Exception as e:
        traceback.print_exc()
        return {"msg": "Lỗi hệ thống", "error": str(e)}, 500
    except Exception as e:
        traceback.print_exc()
        return {"msg": "Lỗi hệ thống", "error": str(e)}, 500
    
@course_bp.route("/lessons/<int:lesson_id>", methods=["PATCH"])
@doc(description="Cập nhật bài học", tags=["Course"])
# @use_kwargs(LessonSchema, location="form")
@teacher_required
def update_lesson(lesson_id):
    try:
        lesson = course_services.get_lesson_by_id(lesson_id)
        if not lesson:
            return {"msg": "Không tìm thấy bài học"}, 404

        data = request.form
        file = request.files.get("file")

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
        lesson_type = data.get("type", lesson.type) 
        upload_file = request.files.get("file")
        if upload_file:
            ext = _get_extension(upload_file.filename)

            if lesson_type == Type.VIDEO.value:
                if ext not in ALLOWED_VIDEO_EXT:
                    return {"msg": "Định dạng video không hỗ trợ"}, 400
                result = cloudinary.uploader.upload(
                    upload_file,
                    resource_type="video",
                    folder="lessons/videos"
                )
            elif lesson_type == Type.FILE.value:
                if ext not in ALLOWED_FILE_EXT:
                    return {"msg": "Định dạng tệp không hỗ trợ"}, 400
                result = cloudinary.uploader.upload(
                    upload_file,
                    resource_type="raw",
                    folder="lessons/files"
                )
            elif lesson_type == Type.IMAGE.value:
                if ext not in ALLOWED_IMAGE_EXT:
                    return {"msg": "Định dạng ảnh không hỗ trợ"}, 400
                result = cloudinary.uploader.upload(
                    upload_file,
                    resource_type="image",
                    folder="lessons/images"
                )
            else:
                return {"msg": "Loại bài học không yêu cầu file"}, 400
            lesson.content_url = result["secure_url"]
        # if file and file.filename::
        #     # Upload lại nếu có file mới
        #     resource_type = "video" if lesson.type == "video" else "raw"
        #     result = cloudinary.uploader.upload(file, resource_type=resource_type)
        #     lesson.content_url = result["secure_url"]

        db.session.commit()
        return {"msg": "Cập nhật bài học thành công"}, 200
    except Exception as e:
        traceback.print_exc()
        return {"msg": "Lỗi hệ thống", "error": str(e)}, 500


@course_bp.route("/lesson/<int:lesson_id>", methods=["DELETE"])
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
    

@course_bp.route("/stats/total-students", methods=["GET"],provide_automatic_options=False)
@doc(description="Thống kê tổng số học viên của giáo viên", tags=["Course Stats"])
@teacher_required
def get_total_students():
    try:
        teacher_id = get_jwt_identity()
        total = course_services.get_total_students_by_teacher(teacher_id)
        return {"msg": "Thống kê học viên thành công", "total_students": total}, 200
    except Exception as e:
        return {"msg": "Lỗi hệ thống", "error": str(e)}, 500

@course_bp.route("/categories", methods=["GET"])
@doc(description="Danh sách Category", tags=["Course"])
@marshal_with(CategorySchema(many=True),200)
@login_required
def list_categorie():
    try:
        print("HEADERS:", request.headers)
        categories = course_services.get_categories()
        return categories

    except Exception as e:
        traceback.print_exc()
        return {"msg": "Lỗi hệ thống", "error": str(e)}, 500

@course_bp.route("/stats/chapters-lessons", methods=["GET"],provide_automatic_options=False)
@doc(description="Thống kê tổng số chương và bài học", tags=["Course Stats"])
@teacher_required
def get_chapter_lesson_counts():
    try:
        teacher_id = get_jwt_identity()
        result = course_services.get_chapter_lesson_count_by_teacher(teacher_id)
        return {"msg": "Thống kê thành công", "data": result}, 200
    except Exception as e:
        return {"msg": "Lỗi hệ thống", "error": str(e)}, 500

@course_bp.route("/stats/avg-lessons-per-chapter", methods=["GET"],provide_automatic_options=False)
@doc(description="Thống kê trung bình số bài học mỗi chương", tags=["Course Stats"])
@teacher_required
def get_avg_lessons():
    try:
        teacher_id = get_jwt_identity()
        avg = course_services.get_avg_lessons_per_chapter(teacher_id)
        return {"msg": "Thống kê thành công", "average_lessons": avg}, 200
    except Exception as e:
        return {"msg": "Lỗi hệ thống", "error": str(e)}, 500

@course_bp.route("/stats/published-lesson-rate", methods=["GET"],provide_automatic_options=False)
@doc(description="Thống kê tỷ lệ bài học đã xuất bản", tags=["Course Stats"])
@teacher_required
def get_publish_rate():
    try:
        teacher_id = get_jwt_identity()
        data = course_services.get_published_lesson_rate(teacher_id)
        return {"msg": "Thống kê thành công", "data": data}, 200
    except Exception as e:
        return {"msg": "Lỗi hệ thống", "error": str(e)}, 500

@course_bp.route("/stats/avg-rating", methods=["GET"],provide_automatic_options=False)
@doc(description="Thống kê trung bình đánh giá của giáo viên", tags=["Course Stats"])
@teacher_required
def get_avg_rating():
    try:
        teacher_id = get_jwt_identity()
        avg_rating = course_services.get_average_teacher_rating(teacher_id)
        return {"msg": "Thống kê thành công", "avg_rating": avg_rating}, 200
    except Exception as e:
        return {"msg": "Lỗi hệ thống", "error": str(e)}, 500

@course_bp.route("/stats/students-completed-lessons", methods=["GET"],provide_automatic_options=False)
@doc(description="Thống kê số học viên đã hoàn thành ít nhất một bài học", tags=["Course Stats"])
@teacher_required
def get_students_completed_lessons():
    try:
        teacher_id = get_jwt_identity()
        total = course_services.get_students_with_completed_lessons(teacher_id)
        return {"msg": "Thống kê thành công", "students_completed": total}, 200
    except Exception as e:
        return {"msg": "Lỗi hệ thống", "error": str(e)}, 500

# API Enrollment
@course_bp.route("/<int:course_id>/enroll", methods=["POST"])
@doc(description="Đăng ký khóa học với phương thức thanh toán", tags=["Course"])
@use_kwargs(EnrollmentRequestSchema, location="json")
@marshal_with(EnrollmentResponseSchema, code=201)
@student_required
def enroll_course(course_id, **kwargs):
    """
    API đăng ký khóa học cho student
    - Yêu cầu authentication: Student phải đăng nhập (JWT token required)
    - Input: course_id từ URL parameter, payment_method từ request body
    - Body: {"payment_method": "vnpay" hoặc "momo"}
    - Validation: Kiểm tra khóa học tồn tại, student chưa đăng ký trước đó
    - Response: Tạo enrollment record và trả về payment URL theo phương thức được chọn
    """
    try:
        user_id = get_jwt_identity()

        # Lấy payment_method từ kwargs (đã được validate bởi schema)
        payment_method = kwargs.get("payment_method", "").lower()

        # Lấy thông tin course trước
        course = course_services.get_course_by_id(course_id)
        if not course:
            return {"msg": "Không tìm thấy khóa học"}, 404

        # Lấy IP client
        client_ip = request.remote_addr or "127.0.0.1"

        # Tạo order_id trước để lưu vào enrollment
        primary_order_id = payment_services.generate_order_id()

        # Tạo enrollment với order_id (cho phép thanh toán lại nếu chưa thanh toán)
        enrollment, error = enrollment_services.create_enrollment(user_id, course_id, primary_order_id)

        if error:
            return {"msg": error}, 400

        # Kiểm tra xem đây có phải là re-payment không (dựa trên payment_status)
        is_repayment = hasattr(enrollment, '_is_existing') or enrollment.payment_status == False

        # Tạo payment URL theo phương thức được chọn
        payment_info = {}

        if payment_method == "vnpay":
            try:
                # Tạo VNPay payment URL
                vnpay_url, _ = payment_services.create_vnpay_payment_url_with_order_id(
                    user_id, course_id, course.price, primary_order_id, "NCB", client_ip
                )
                payment_info = {
                    "payment_url": vnpay_url,
                    "order_id": primary_order_id,
                    "method": "VNPay",
                    "success": True
                }
            except Exception as e:
                print(f"VNPay URL generation failed: {str(e)}")
                payment_info = {
                    "payment_url": None,
                    "order_id": primary_order_id,
                    "method": "VNPay",
                    "success": False,
                    "error": str(e)
                }

        elif payment_method == "momo":
            try:
                # Tạo MoMo payment URL
                momo_response = payment_services.create_momo_payment_request_with_order_id(
                    user_id, course_id, course.price, primary_order_id
                )
                payment_info = {
                    "payment_url": momo_response.get("payUrl"),
                    "order_id": primary_order_id,
                    "method": "MoMo",
                    "success": momo_response.get("payUrl") is not None,
                    "message": momo_response.get("message")
                }
            except Exception as e:
                print(f"MoMo URL generation failed: {str(e)}")
                payment_info = {
                    "payment_url": None,
                    "order_id": primary_order_id,
                    "method": "MoMo",
                    "success": False,
                    "error": str(e)
                }

        response_data = {
            "id": enrollment.id,
            "course_id": enrollment.course_id,
            "user_id": enrollment.user_id,
            "progress": enrollment.progress,
            "status": enrollment.status,  # unfinished -> completed (based on learning progress)
            "order_id": enrollment.order_id,
            "payment_status": "pending" if not enrollment.payment_status else "paid",
            "message": f"{'Thanh toán lại' if is_repayment else 'Đăng ký khóa học thành công'}. Thanh toán qua {payment_method.upper()}:",
            "course": {
                "id": course.id,
                "title": course.title,
                "price": course.price,
                "description": course.description
            },
            "payment_info": payment_info  # Thông tin thanh toán theo phương thức được chọn
        }

        return response_data, 201

    except Exception as e:
        traceback.print_exc()
        return {"msg": "Lỗi hệ thống", "error": str(e)}, 500

@course_bp.route("/enrollment/order/<string:order_id>", methods=["GET"])
@doc(description="Lấy thông tin enrollment theo order_id", tags=["Course"])
@marshal_with(EnrollmentSchema, code=200)
def get_enrollment_by_order_id(order_id):
    """
    API lấy thông tin enrollment theo order_id
    - Dùng để lấy course_id từ order_id sau khi thanh toán thành công
    - Không yêu cầu authentication vì được gọi từ payment return page
    """
    try:
        enrollment = enrollment_services.get_enrollment_by_order_id(order_id)
        if not enrollment:
            return {"msg": "Không tìm thấy đăng ký khóa học với order_id này"}, 404

        return enrollment, 200

    except Exception as e:
        traceback.print_exc()
        return {"msg": "Lỗi hệ thống", "error": str(e)}, 500

# thêm vào swagger-ui
#đăng kí các hàm ở đây để hiện lên swagger
def course_register_docs(docs):
    docs.register(list_courses, blueprint='course')
    docs.register(get_course_detail, blueprint='course')
    docs.register(get_courses_by_teacher, blueprint='course')
    docs.register(list_teacher_courses_not_public, blueprint='course')
    docs.register(list_teacher_courses_public, blueprint='course')
    
    docs.register(get_courses_by_category, blueprint='course')
    docs.register(get_courses_by_student, blueprint='course')
    docs.register(get_course_chapters, blueprint='course')
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
    docs.register(get_total_students, blueprint='course')
    docs.register(get_chapter_lesson_counts, blueprint='course')
    docs.register(get_avg_lessons, blueprint='course')
    docs.register(get_publish_rate, blueprint='course')
    docs.register(get_avg_rating, blueprint='course')
    docs.register(get_students_completed_lessons, blueprint='course')

    docs.register(list_categorie, blueprint='course')
    docs.register(enroll_course, blueprint='course')
    docs.register(get_enrollment_by_order_id, blueprint='course')

