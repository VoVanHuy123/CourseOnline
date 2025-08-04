from marshmallow import Schema, fields, validate

class EmailConfigSchema(Schema):
    smtp_server = fields.Str(required=True)
    smtp_port = fields.Int(required=True, validate=validate.Range(min=1, max=65535))
    smtp_username = fields.Str(required=True)
    smtp_password = fields.Str(required=True)
    from_email = fields.Email(required=True)

class EmailSendRequestSchema(Schema):
    to_email = fields.Email(required=True)
    subject = fields.Str(required=True, validate=validate.Length(min=1, max=200))
    content = fields.Str(required=True, validate=validate.Length(min=1))
    is_html = fields.Bool(missing=False)

class EmailSendResponseSchema(Schema):
    success = fields.Bool(required=True)
    message = fields.Str(required=True)
    email_id = fields.Str(allow_none=True)

class InvoiceEmailRequestSchema(Schema):
    enrollment_id = fields.Int(required=True)
    force_resend = fields.Bool(missing=False)

class InvoiceEmailResponseSchema(Schema):
    success = fields.Bool(required=True)
    message = fields.Str(required=True)
    enrollment_id = fields.Int(required=True)
    email_sent_to = fields.Email(allow_none=True)
