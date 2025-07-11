
from flask import Blueprint,request
from app.schemas.comment import  LessonCommentSchema,LessonCommentResponseSchema
from webargs.flaskparser import use_kwargs
from flask_apispec import doc, marshal_with,use_kwargs
from app.perms.perms import login_required,student_required,owner_required
from flask_jwt_extended import  get_jwt_identity
from app.services import comment_services 
from app.models.course import LessonComment
import traceback


comment_bp = Blueprint("comment", __name__,url_prefix="/comments")


from marshmallow import fields

@comment_bp.route("/", methods=["GET"],provide_automatic_options=False)
@doc(description="Lấy danh sách comment theo lesson_id", tags=["LessonComment"])
@use_kwargs({"lesson_id": fields.Int(required=True)}, location="query")
@marshal_with(LessonCommentResponseSchema(many=True))
@login_required
def list_lesson_comments(lesson_id):
    comments = comment_services.get_lesson_comments(lesson_id)
    return comments, 200


@comment_bp.route("/", methods=["POST"],provide_automatic_options=False)
@doc(description="Tạo bình luận bài học", tags=["LessonComment"])
@use_kwargs(LessonCommentSchema, location="json")
@marshal_with(LessonCommentResponseSchema, code=201)
@login_required
def create_lesson_comment(**kwargs):
    user_id = get_jwt_identity()
    kwargs["user_id"] = user_id
    comment = comment_services.create_lesson_comment(**kwargs)
    return comment, 201

@comment_bp.route("/<int:id>", methods=["PUT"],provide_automatic_options=False)
@doc(description="Cập nhật bình luận", tags=["LessonComment"])
@use_kwargs(LessonCommentSchema, location="json")
@marshal_with(LessonCommentResponseSchema)
@login_required
@owner_required(model=LessonComment, lookup_arg="id")
def update_lesson_comment(id, **kwargs):
    comment = LessonComment.query.get_or_404(id)
    comment_services.update_comment(comment,**kwargs)
    return comment

@comment_bp.route("/<int:id>", methods=["DELETE"],provide_automatic_options=False)
@doc(description="Xóa bình luận", tags=["LessonComment"])
@login_required
@owner_required(model=LessonComment, lookup_arg="id")
def delete_lesson_comment(id):
    comment = LessonComment.query.get_or_404(id)
    comment_services.delete_comment(comment)
    return {"msg": "Deleted"}, 200

def comment_register_docs(docs):
    docs.register(create_lesson_comment, blueprint='comment')
    docs.register(list_lesson_comments, blueprint='comment')
    docs.register(update_lesson_comment, blueprint='comment')
    docs.register(delete_lesson_comment, blueprint='comment')