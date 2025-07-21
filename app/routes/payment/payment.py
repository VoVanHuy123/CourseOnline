import os
import hashlib
import hmac
from urllib.parse import urlencode
from flask_apispec import use_kwargs, marshal_with, doc
from flask import Blueprint, request, redirect, current_app
from app.services.course_services import get_course_by_id
from werkzeug.exceptions import NotFound
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# ====== Thông số cấu hình lấy từ .env ======
VNP_TMN_CODE   = os.getenv("VNPAY_TMN_CODE")
VNP_HASH_SECRET = os.getenv("VNPAY_HASH_SECRET_KEY")
VNP_URL        = os.getenv("VNPAY_PAYMENT_URL")      # sandbox: https://sandbox.vnpayment.vn/paymentv2/vpcpay.html
VNP_RETURN_URL = os.getenv("VNPAY_RETURN_URL")       # ví dụ: https://abc.ngrok.app/payment/vnpay/return

# ====== Blueprint khai báo ======
payment_bp = Blueprint("payment", __name__, url_prefix="/payment")

# ---------- 1. Tạo URL thanh toán ----------
@payment_bp.route("/vnpay", methods=["POST"], provide_automatic_options=False)
@doc(description="Xóa bài học", tags=["Payment"])
def create_vnpayment():
    """
    Nhận dữ liệu từ client (order_id, amount, bank_code...)
    và redirect sang trang thanh toán VNPAY
    """
    body = request.get_json(silent=True) or {}

    order_id   = body.get("order_id", "order123")
    amount_vnd = int(body.get("amount", 100_000))  # 100k VNĐ mặc định
    bank_code  = body.get("bank_code", "NCB")

    # Flask: lấy IP client
    client_ip = request.remote_addr or "127.0.0.1"

    # ------- 3.1 Lấy course -------
    course_id = body.get("course_id")
    if not course_id:
        return {"msg": "course_id là bắt buộc"}, 400

    course = get_course_by_id(course_id)
    if not course:
        raise NotFound(description="Không tìm thấy khoá học")

    params = {
        "vnp_Version":  "2.1.0",
        "vnp_Command":  "pay",
        "vnp_TmnCode":  VNP_TMN_CODE,
        "vnp_Amount":   str(amount_vnd * 100),          # nhân 100 theo quy định VNPAY
        "vnp_CurrCode": "VND",
        "vnp_TxnRef":   order_id,                      # mã giao dịch
        "vnp_OrderInfo": f"Thanh toan khoa hoc #{order_id}",
        "vnp_OrderType": "other",
        "vnp_Locale":   "vn",
        "vnp_BankCode": bank_code,
        "vnp_CreateDate": datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S"),
        "vnp_IpAddr":   client_ip,
        "vnp_ReturnUrl": VNP_RETURN_URL,
    }

    # ----- 1.1 Tạo chuỗi query đã sort -----
    sorted_items   = sorted(params.items())                # sort key ASC
    query_string   = urlencode(sorted_items)

    # ----- 1.2 Tính chữ ký SHA‑512 -----
    sign_data = "&".join(f"{k}={v}" for k, v in sorted_items)
    secure_hash = hmac.new(
        VNP_HASH_SECRET.encode(),
        sign_data.encode(),
        hashlib.sha512
    ).hexdigest()

    # ----- 1.3 Ghép URL cuối cùng -----
    payment_url = f"{VNP_URL}?{query_string}&vnp_SecureHash={secure_hash}"

    current_app.logger.info("Redirect VNPAY URL: %s", payment_url)
    return redirect(payment_url, code=302)


# ---------- 2. Xử lý return_url ----------
@payment_bp.route("/vnpay/return")
@doc(description="Xóa bài học", tags=["Payment"])
def vnpay_return():
    """ Xác thực chữ ký khi VNPAY redirect về """
    params = dict(request.args)
    vnp_secure_hash = params.pop("vnp_SecureHash", None)
    sorted_items = sorted(params.items())
    sign_data    = "&".join(f"{k}={v}" for k, v in sorted_items)

    check_hash = hmac.new(
        VNP_HASH_SECRET.encode(),
        sign_data.encode(),
        hashlib.sha512
    ).hexdigest()

    if check_hash != vnp_secure_hash:
        return {"code": "97", "message": "Invalid signature"}, 400

    # TODO: xử lý cập nhật đơn hàng tại đây
    return {"code": "00", "message": "Payment success"}, 200


# ---------- 3. Đăng ký với Flask‑Apispec ----------
def payment_register_docs(docs):
    docs.register(create_vnpayment, blueprint="payment")
    docs.register(vnpay_return,     blueprint="payment")
