from marshmallow import Schema, fields, validate

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