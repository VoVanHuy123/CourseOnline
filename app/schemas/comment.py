from marshmallow import Schema, fields, validate
from .user import UserCommentSchema

class LessonCommentSchema(Schema):
    content = fields.Str(required=True, validate=validate.Length(min=1))
    lesson_id = fields.Int(required=True)
    reply_to = fields.Int(required=False,allow_none=True)

class LessonCommentResponseSchema(Schema):
    id = fields.Int()
    content = fields.Str()
    lesson_id = fields.Int()
    user = fields.Nested(UserCommentSchema, attribute="user",dump_only=True)  # ánh xạ tới relationship user trong model

    reply_to = fields.Int(allow_none=True)
    replies = fields.List(fields.Nested(lambda: LessonCommentResponseSchema(exclude=("replies",)))) # đệ quy