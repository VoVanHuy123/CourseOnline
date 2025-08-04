from flask import Blueprint, request
from flask_apispec import use_kwargs, marshal_with, doc
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.schemas.email import (
    InvoiceEmailRequestSchema, 
    InvoiceEmailResponseSchema,
    EmailSendRequestSchema,
    EmailSendResponseSchema
)
from app.services.email_services import email_service
from app.services import enrollment_services
from app.models.course import Enrollment, Course
from app.models.user import User
from app.perms.perms import admin_required, student_required
import traceback
import logging

logger = logging.getLogger(__name__)

email_bp = Blueprint("email", __name__, url_prefix="/email")

@email_bp.route("/invoice/send", methods=["POST"])
@doc(description="Gửi email hóa đơn cho enrollment cụ thể", tags=["Email"])
@use_kwargs(InvoiceEmailRequestSchema, location="json")
@marshal_with(InvoiceEmailResponseSchema, code=200)
@admin_required
def send_invoice_email(**kwargs):
    """
    API gửi email hóa đơn cho enrollment cụ thể
    - Chỉ admin mới có thể gọi API này
    - Có thể force resend nếu cần
    """
    try:
        enrollment_id = kwargs.get("enrollment_id")
        force_resend = kwargs.get("force_resend", False)
        
        # Lấy enrollment
        enrollment = Enrollment.query.get(enrollment_id)
        if not enrollment:
            return {
                "success": False,
                "message": "Không tìm thấy enrollment",
                "enrollment_id": enrollment_id,
                "email_sent_to": None
            }, 404
        
        # Kiểm tra đã thanh toán chưa
        if not enrollment.payment_status:
            return {
                "success": False,
                "message": "Enrollment chưa được thanh toán",
                "enrollment_id": enrollment_id,
                "email_sent_to": None
            }, 400
        
        # Lấy user email
        user = User.query.get(enrollment.user_id)
        if not user:
            return {
                "success": False,
                "message": "Không tìm thấy user",
                "enrollment_id": enrollment_id,
                "email_sent_to": None
            }, 404
        
        # Gửi email
        success = enrollment_services.send_payment_invoice_email(enrollment)
        
        return {
            "success": success,
            "message": "Email đã được gửi thành công" if success else "Gửi email thất bại",
            "enrollment_id": enrollment_id,
            "email_sent_to": user.email if success else None
        }, 200
        
    except Exception as e:
        logger.error(f"Error in send_invoice_email: {str(e)}")
        traceback.print_exc()
        return {
            "success": False,
            "message": f"Lỗi hệ thống: {str(e)}",
            "enrollment_id": kwargs.get("enrollment_id", 0),
            "email_sent_to": None
        }, 500

@email_bp.route("/invoice/resend/<int:enrollment_id>", methods=["POST"])
@doc(description="Gửi lại email hóa đơn cho enrollment", tags=["Email"])
@marshal_with(InvoiceEmailResponseSchema, code=200)
@admin_required
def resend_invoice_email(enrollment_id):
    """
    API gửi lại email hóa đơn cho enrollment
    - Chỉ admin mới có thể gọi API này
    """
    try:
        # Lấy enrollment
        enrollment = Enrollment.query.get(enrollment_id)
        if not enrollment:
            return {
                "success": False,
                "message": "Không tìm thấy enrollment",
                "enrollment_id": enrollment_id,
                "email_sent_to": None
            }, 404
        
        # Kiểm tra đã thanh toán chưa
        if not enrollment.payment_status:
            return {
                "success": False,
                "message": "Enrollment chưa được thanh toán",
                "enrollment_id": enrollment_id,
                "email_sent_to": None
            }, 400
        
        # Lấy user email
        user = User.query.get(enrollment.user_id)
        if not user:
            return {
                "success": False,
                "message": "Không tìm thấy user",
                "enrollment_id": enrollment_id,
                "email_sent_to": None
            }, 404
        
        # Gửi email
        success = enrollment_services.send_payment_invoice_email(enrollment)
        
        return {
            "success": success,
            "message": "Email đã được gửi lại thành công" if success else "Gửi lại email thất bại",
            "enrollment_id": enrollment_id,
            "email_sent_to": user.email if success else None
        }, 200
        
    except Exception as e:
        logger.error(f"Error in resend_invoice_email: {str(e)}")
        traceback.print_exc()
        return {
            "success": False,
            "message": f"Lỗi hệ thống: {str(e)}",
            "enrollment_id": enrollment_id,
            "email_sent_to": None
        }, 500

@email_bp.route("/test", methods=["POST"])
@doc(description="Test gửi email", tags=["Email"])
@use_kwargs(EmailSendRequestSchema, location="json")
@marshal_with(EmailSendResponseSchema, code=200)
@admin_required
def test_email(**kwargs):
    """
    API test gửi email
    - Chỉ admin mới có thể gọi API này
    - Dùng để test cấu hình email
    """
    try:
        to_email = kwargs.get("to_email")
        subject = kwargs.get("subject")
        content = kwargs.get("content")
        is_html = kwargs.get("is_html", False)
        
        # Test gửi email đơn giản
        if is_html:
            success = email_service._send_email(to_email, subject, content)
        else:
            # Convert plain text to simple HTML
            html_content = f"<html><body><p>{content}</p></body></html>"
            success = email_service._send_email(to_email, subject, html_content)
        
        return {
            "success": success,
            "message": "Email test đã được gửi thành công" if success else "Gửi email test thất bại",
            "email_id": None
        }, 200
        
    except Exception as e:
        logger.error(f"Error in test_email: {str(e)}")
        traceback.print_exc()
        return {
            "success": False,
            "message": f"Lỗi hệ thống: {str(e)}",
            "email_id": None
        }, 500

def email_register_docs(docs):
    """Đăng ký các API endpoints vào swagger documentation"""
    docs.register(send_invoice_email, blueprint='email')
    docs.register(resend_invoice_email, blueprint='email')
    docs.register(test_email, blueprint='email')
