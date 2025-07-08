from marshmallow import Schema, fields

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
    
class CourseSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True) 
    description = fields.Str()
    image = fields.Str(required=False)
    price = fields.Float()
    teacher_id = fields.Int()
    category_id = fields.Int()
    is_public=fields.Boolean()  
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

class ChapterSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True)
    description = fields.Str()
    course_id = fields.Int(required=True)
    lessons = fields.List(fields.Nested('LessonNameSchema'), dump_only=True)

class LessonNameSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True)
    description = fields.Str(required=True)


class LessonSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True)
    description = fields.Str(required=True)
    type  = fields.Str(required=True)
    content_url = fields.Str(required=False)
    image = fields.Str()
    is_published = fields.Boolean()
    order = fields.Int()
    is_locked = fields.Boolean()
    chapter_id = fields.Int()