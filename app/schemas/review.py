from marshmallow import Schema, fields, validate
from .user import UserCommentSchema

class CourseReviewSchema(Schema):
    comment = fields.Str(required=True, validate=validate.Length(min=1))
    rating = fields.Int(required=False, validate=validate.Range(min=1, max=5))
    course_id = fields.Int(required=True)
    

class CourseReviewResponseSchema(Schema):
    id = fields.Int()
    comment = fields.Str()
    rating = fields.Int()
    course_id = fields.Int()
    user = fields.Nested(UserCommentSchema, attribute="user",dump_only=True)
    user_id = fields.Int()

class LessonCommentSchema(Schema):
    content = fields.Str(required=True, validate=validate.Length(min=1))
    lesson_id = fields.Int(required=True)
    
    reply_to = fields.Int(allow_none=True)

class LessonCommentResponseSchema(Schema):
    id = fields.Int()
    content = fields.Str()
    lesson_id = fields.Int()
    user_id = fields.Int()
    reply_to = fields.Int(allow_none=True)