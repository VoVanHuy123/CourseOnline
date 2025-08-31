from urllib.parse import urlencode
from flask_apispec import use_kwargs, marshal_with, doc
from flask import Blueprint, request, redirect, current_app, jsonify
from flask_jwt_extended import get_jwt_identity
from app.services.course_services import get_course_by_id
from app.services import payment_services, enrollment_services
from app.schemas.payment import PaymentRequestSchema, VNPayPaymentResponseSchema, MoMoPaymentResponseSchema, PaymentIPNSchema
from app.perms.perms import student_required
from werkzeug.exceptions import NotFound
from datetime import datetime
from dotenv import load_dotenv
import traceback

load_dotenv()

payment_bp = Blueprint("payment", __name__, url_prefix="/payment")

@payment_bp.route("/vnpay", methods=["POST"])
@doc(description="Tạo payment request với VNPay", tags=["Payment"])
@use_kwargs(PaymentRequestSchema, location="json")
@marshal_with(VNPayPaymentResponseSchema, code=200)
@student_required
def create_vnpayment(**kwargs):
    """
    Tạo payment request với VNPay
    - Yêu cầu student đã đăng ký khóa học (enrollment tồn tại và chưa thanh toán)
    - Tạo URL thanh toán VNPay
    """
    try:
        user_id = get_jwt_identity()
        course_id = kwargs.get("course_id")
        amount = kwargs.get("amount")
        bank_code = kwargs.get("bank_code", "NCB")
        
        # Kiểm tra enrollment tồn tại và chưa thanh toán
        enrollment = enrollment_services.get_enrollment_by_user_and_course(user_id, course_id)
        if not enrollment:
            return {"message": "Bạn chưa đăng ký khóa học này"}, 400

        if enrollment.payment_status == True:
            return {"message": "Khóa học này đã được thanh toán"}, 400
        
        # Kiểm tra khóa học tồn tại
        course = get_course_by_id(course_id)
        if not course:
            return {"message": "Không tìm thấy khóa học"}, 404
        
        # Kiểm tra amount có khớp với giá khóa học không
        if amount != course.price:
            return {"message": f"Số tiền không đúng. Giá khóa học là {course.price} VND"}, 400
        
        # Lấy IP client
        client_ip = request.remote_addr or "127.0.0.1"
        
        # Tạo URL thanh toán
        payment_url, order_id = payment_services.create_vnpay_payment_url(
            user_id, course_id, amount, bank_code, client_ip
        )
        
        return {
            "payment_url": payment_url,
            "order_id": order_id,
            "message": "Tạo URL thanh toán thành công"
        }, 200
        
    except Exception as e:
        traceback.print_exc()
        return {"message": "Lỗi hệ thống", "error": str(e)}, 500

@payment_bp.route("/vnpay/ipn", methods=["GET", "POST"])
@doc(description="Webhook IPN từ VNPay", tags=["Payment"])
@marshal_with(PaymentIPNSchema, code=200)
def vnpay_ipn():
    """
    Webhook nhận thông báo từ VNPay
    - Xác thực chữ ký
    - Cập nhật enrollment status khi thanh toán thành công
    """
    try:
        # VNPay có thể gửi IPN qua GET hoặc POST
        if request.method == "GET":
            params = dict(request.args)
            print(f"VNPay IPN - Received GET request with params: {params}")
        else:
            params = dict(request.form) if request.form else dict(request.args)
            print(f"VNPay IPN - Received POST request with params: {params}")

        if not params:
            print("VNPay IPN - No parameters received")
            return {"RspCode": "99", "Message": "No parameters"}, 400

        # Xử lý IPN
        response = payment_services.process_vnpay_ipn(params)

        print(f"VNPay IPN - Sending response: {response}")
        return response, 200

    except Exception as e:
        print(f"VNPay IPN - Exception occurred: {str(e)}")
        traceback.print_exc()
        return {"RspCode": "99", "Message": "System error"}, 500

@payment_bp.route("/momo", methods=["POST"])
@doc(description="Tạo payment request với MoMo", tags=["Payment"])
@use_kwargs(PaymentRequestSchema, location="json")
@marshal_with(MoMoPaymentResponseSchema, code=200)
@student_required
def create_momo_payment(**kwargs):
    """
    Tạo payment request với MoMo
    - Yêu cầu student đã đăng ký khóa học (enrollment tồn tại và chưa thanh toán)
    - Tạo payment request MoMo
    """
    try:
        user_id = get_jwt_identity()
        course_id = kwargs.get("course_id")
        amount = kwargs.get("amount")
        
        # Kiểm tra enrollment tồn tại và chưa thanh toán
        enrollment = enrollment_services.get_enrollment_by_user_and_course(user_id, course_id)
        if not enrollment:
            return {"message": "Bạn chưa đăng ký khóa học này"}, 400

        if enrollment.payment_status == True:
            return {"message": "Khóa học này đã được thanh toán"}, 400
        
        # Kiểm tra khóa học tồn tại
        course = get_course_by_id(course_id)
        if not course:
            return {"message": "Không tìm thấy khóa học"}, 404
        
        # Kiểm tra amount có khớp với giá khóa học không
        if amount != course.price:
            return {"message": f"Số tiền không đúng. Giá khóa học là {course.price} VND"}, 400
        
        # Tạo payment request với MoMo
        response = payment_services.create_momo_payment_request(user_id, course_id, amount)
        
        return response, 200
        
    except Exception as e:
        traceback.print_exc()
        return {"message": "Lỗi hệ thống", "error": str(e)}, 500

@payment_bp.route("/momo/ipn", methods=["POST"])
@doc(description="Webhook IPN từ MoMo", tags=["Payment"])
@marshal_with(PaymentIPNSchema, code=200)
def momo_ipn():
    """
    Webhook nhận thông báo từ MoMo
    - Xác thực chữ ký
    - Cập nhật enrollment status khi thanh toán thành công
    """
    try:
        params = request.get_json() or {}
        
        # Xử lý IPN
        response = payment_services.process_momo_ipn(params)
        
        return response, 200
        
    except Exception as e:
        traceback.print_exc()
        return {"resultCode": 99, "message": "System error"}, 500

# Đăng ký docs
def payment_register_docs(docs):
    docs.register(create_vnpayment, blueprint='payment')
    docs.register(vnpay_ipn, blueprint='payment')
    docs.register(create_momo_payment, blueprint='payment')
    docs.register(momo_ipn, blueprint='payment')
