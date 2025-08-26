from marshmallow import Schema, fields, validate
from app.models.course import Type

class CourseCreateResponseSchema(Schema):
    msg = fields.Str(example="Tạo khoá học thành công")
    course_title = fields.Str(example="Python cơ bản")
class ChapterCreateResponseSchema(Schema):
    msg = fields.Str(example="Tạo chương thành công")
    chapter_title = fields.Str(example="Python cơ bản")
class LessonCreateResponseSchema(Schema):
    msg = fields.Str(example="Tạo bài học thành công")
    lesson_title = fields.Str(example="Python cơ bản")
    lesson_id = fields.Int(example=0)
    
class EnrollmentStatusSchema(Schema):
    is_enrolled = fields.Bool()
    payment_status = fields.Bool()
    progress = fields.Float()
    status = fields.Str(allow_none=True)

class CourseSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True)
    description = fields.Str()
    image = fields.Str(required=False)
    price = fields.Float()
    teacher_id = fields.Int()
    category_id = fields.Int()
    is_public=fields.Boolean()
    is_sequential=fields.Boolean()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    enrollment_status = fields.Nested(EnrollmentStatusSchema, dump_only=True)

class ChapterSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True)
    description = fields.Str()
    course_id = fields.Int(required=True)
    order = fields.Int(required=True)
    lessons = fields.List(fields.Nested('LessonNameSchema'), dump_only=True)
class ListChapterSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True)
    description = fields.Str()
    # course_id = fields.Int(required=True)
    order = fields.Int(required=True)
    lessons = fields.List(fields.Nested('LessonInChapterDumpSchema'), dump_only=True)

class LessonNameSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True)
    description = fields.Str(required=True)

class LessonInChapterDumpSchema(Schema):
    id           = fields.Int(dump_only=True)
    title        = fields.Str(required=True)
    description  = fields.Str(required=True)
    type         = fields.Str(required=True, validate=lambda v: v in Type._value2member_map_)
    chapter_id   = fields.Int(required=True)
    order        = fields.Int()
    content_url = fields.Str(required=False)
    is_published = fields.Bool()
class LessonSchema(Schema):
    id           = fields.Int(dump_only=True)
    title        = fields.Str(required=True)
    description  = fields.Str(required=True)
    type         = fields.Str(required=True, validate=lambda v: v in Type._value2member_map_)
    chapter_id   = fields.Int(required=True)
    order        = fields.Int()
    is_published = fields.Bool()

class LessonProgressSchema(Schema):
    lesson_id = fields.Int(required=True)
    is_completed = fields.Boolean(required=True)

class EnrollmentSchema(Schema):
    id = fields.Int(dump_only=True)
    course_id = fields.Int(required=True)
    user_id = fields.Int(dump_only=True)
    progress = fields.Float(dump_only=True)
    status = fields.Str(dump_only=True)
    payment_status = fields.Bool(dump_only=True)
    created_day = fields.DateTime(dump_only=True)

class EnrollmentRequestSchema(Schema):
    payment_method = fields.Str(required=True, validate=validate.OneOf(["vnpay", "momo"]))

class PaymentInfoSchema(Schema):
    payment_url = fields.Str(allow_none=True)
    order_id = fields.Str(allow_none=True)
    method = fields.Str()
    success = fields.Bool()
    message = fields.Str(missing="")
    error = fields.Str(missing="")

class EnrollmentResponseSchema(Schema):
    id = fields.Int()
    course_id = fields.Int()
    user_id = fields.Int()
    progress = fields.Float()
    status = fields.Str()
    order_id = fields.Str()
    payment_status = fields.Str()
    message = fields.Str()
    course = fields.Nested(CourseSchema, dump_only=True)
    payment_info = fields.Nested(PaymentInfoSchema, dump_only=True)  # Thông tin thanh toán theo phương thức được chọn

class CategorySchema(Schema):
    id = fields.Int(required=True)
    name = fields.Str(required=True)

from marshmallow import Schema, fields
from .user import UserSchema  # nếu bạn muốn nested user

class LessonHistoryListSchema(Schema):
    id = fields.Int(dump_only=True)
    action = fields.Str(required=True)
    created_at = fields.DateTime(dump_only=True)
    lesson_id = fields.Int()

class LessonHistorySchema(Schema):
    id = fields.Int(dump_only=True)
    action = fields.Str(required=True)  # 'create' hoặc 'update'
    title = fields.Str()
    description = fields.Str()
    type = fields.Str()   # Enum Type (text/video/file/image)
    content_url = fields.Str()
    image = fields.Str()
    is_published = fields.Boolean()
    order = fields.Int()
    is_locked = fields.Boolean()
    created_at = fields.DateTime(dump_only=True)

    # nested relationships
    lesson_id = fields.Int()
    user_id = fields.Int()
    # user = fields.Nested(UserSchema, dump_only=True)  # nếu muốn trả thông tin user luôn