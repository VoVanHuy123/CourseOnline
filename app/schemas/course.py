from marshmallow import Schema, fields

class CourseSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True) 
    description = fields.Str()
    price = fields.Float()
    teacher_id = fields.Int()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)