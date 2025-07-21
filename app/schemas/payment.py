from marshmallow import Schema, fields, validate

class PaymentRequestSchema(Schema):
    course_id = fields.Int(required=True)
    amount = fields.Float(required=True, validate=validate.Range(min=0))
    bank_code = fields.Str(missing="NCB")  # Mặc định NCB cho VNPay

class VNPayPaymentResponseSchema(Schema):
    payment_url = fields.Str()
    order_id = fields.Str()
    message = fields.Str()

class MoMoPaymentResponseSchema(Schema):
    payUrl = fields.Str()
    orderId = fields.Str()
    message = fields.Str()

class PaymentIPNSchema(Schema):
    """Schema cho IPN response"""
    RspCode = fields.Str()  # VNPay
    Message = fields.Str()  # VNPay
    resultCode = fields.Int()  # MoMo
    message = fields.Str()  # MoMo
