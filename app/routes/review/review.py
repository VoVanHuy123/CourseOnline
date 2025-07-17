from flask import Blueprint,request
from app.models.course import CourseReview
from app.schemas.review import CourseReviewSchema, CourseReviewResponseSchema , LessonCommentSchema,LessonCommentResponseSchema
from webargs.flaskparser import use_kwargs
from flask_apispec import doc, marshal_with,use_kwargs
from app.perms.perms import login_required,student_required,owner_required
from flask_jwt_extended import  get_jwt_identity
from app.services import review_service, user_services
import traceback
# from app.extensions im

review_bp = Blueprint("review", __name__,url_prefix="/reviews")

@review_bp.route("/", methods=["GET"], provide_automatic_options=False)
@doc(description="Lấy danh sách review khóa học", tags=["CourseReview"])
@marshal_with(CourseReviewResponseSchema(many=True))
@student_required
# http://127.0.0.1:5000/reviews?course_id=1
def get_reviews():
    course_id = request.args.get("course_id")
    if not course_id:
        return {"msg": "Thiếu course_id trong query params"}, 400
    try:
        course_reviews = review_service.get_course_reviews_parent(course_id)
        return course_reviews, 200
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"msg": "Lỗi hệ thống", "error": str(e)}, 500

@review_bp.route("/", methods=["POST"])
@doc(description="Tạo review khóa học", tags=["CourseReview"])
@use_kwargs(CourseReviewSchema, location="json")
@marshal_with(CourseReviewResponseSchema, code=201)
@student_required
def create_review(**kwargs):
    user_id = get_jwt_identity()
    user = user_services.get_user_by_id(user_id)
    if not user:
        return {"msg": "Không tìm thấy người dùng tương ứng"}, 404
    kwargs["user_id"] = user_id

    review = review_service.create_course_review(**kwargs)
    return review, 201

@review_bp.route("/<int:id>", methods=["PUT"])
@doc(description="Cập nhật review", tags=["CourseReview"])
@use_kwargs(CourseReviewSchema, location="json")
@marshal_with(CourseReviewResponseSchema)
@student_required
@owner_required(model=CourseReview,lookup_arg="id") # kiểm tra quyền sở hữu
def update_review(id, **kwargs):
    try:
        review = review_service.get_course_review_by_id(id)
        review = review_service.update_course_review(review,**kwargs)
        return review
    except Exception as e:
        traceback.print_exc()
        return {"msg": "Lỗi hệ thống", "error": str(e)}, 500
@review_bp.route("/<int:id>", methods=["DELETE"])
@doc(description="Xóa review", tags=["CourseReview"])
@login_required
@owner_required(model=CourseReview,lookup_arg="id")
def delete_review(id):
    try:

        review = review_service.get_course_review_by_id(id)
        review_service.delete_course_review(review)
        return {"message": "Deleted successfully"}, 200
    except Exception as e:
        traceback.print_exc()
        return {"msg": "Lỗi hệ thống", "error": str(e)}, 500
    




def review_register_docs(docs):
    docs.register(get_reviews, blueprint='review')
    docs.register(create_review, blueprint='review')
    docs.register(update_review, blueprint='review')
    docs.register(delete_review, blueprint='review')