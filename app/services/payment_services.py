import hashlib
import hmac
import json
import uuid
import urllib.parse
import requests
import os
from datetime import datetime
from urllib.parse import urlencode
from flask import current_app
from dotenv import load_dotenv
from app.services.enrollment_services import update_enrollment_payment_status, update_enrollment_payment_status_by_order_id
import logging

logger = logging.getLogger(__name__)
load_dotenv()

class Vnpay:
    """VNPay Official SDK Class"""
    responseData = {}

    def __init__(self, tmn_code, secret_key, return_url, vnpay_payment_url, api_url):
        self.tmn_code = tmn_code
        self.secret_key = secret_key
        self.return_url = return_url
        self.vnpay_payment_url = vnpay_payment_url
        self.api_url = api_url

    def get_payment_url(self, requestData):
        inputData = sorted(requestData.items())
        queryString = ''
        hasData = ''
        seq = 0
        for key, val in inputData:
            if seq == 1:
                queryString = queryString + "&" + key + '=' + urllib.parse.quote_plus(str(val))
            else:
                seq = 1
                queryString = key + '=' + urllib.parse.quote_plus(str(val))

        hashValue = self.__hmacsha512(self.secret_key, queryString)
        return self.vnpay_payment_url + "?" + queryString + '&vnp_SecureHash=' + hashValue

    def validate_response(self, responseData):
        vnp_SecureHash = responseData['vnp_SecureHash']
        
        if 'vnp_SecureHash' in responseData.keys():
            responseData.pop('vnp_SecureHash')

        if 'vnp_SecureHashType' in responseData.keys():
            responseData.pop('vnp_SecureHashType')

        inputData = sorted(responseData.items())
        hasData = ''
        seq = 0
        for key, val in inputData:
            if str(key).startswith('vnp_'):
                if seq == 1:
                    hasData = hasData + "&" + str(key) + '=' + urllib.parse.quote_plus(str(val))
                else:
                    seq = 1
                    hasData = str(key) + '=' + urllib.parse.quote_plus(str(val))
        hashValue = self.__hmacsha512(self.secret_key, hasData)


        return vnp_SecureHash == hashValue

    @staticmethod
    def __hmacsha512(key, data):
        byteKey = key.encode('utf-8')
        byteData = data.encode('utf-8')
        return hmac.new(byteKey, byteData, hashlib.sha512).hexdigest()

def generate_order_id():
    """Tạo order ID unique"""
    return f"{uuid.uuid4().hex[:8].upper()}"

def create_vnpay_payment_url(user_id, course_id, amount, bank_code="NCB", client_ip="127.0.0.1"):
    """Tạo URL thanh toán VNPay"""
    order_id = generate_order_id()

    # Get configuration from environment variables
    vnp_tmn_code = os.getenv("VNPAY_TMN_CODE")
    vnp_hash_secret = os.getenv("VNPAY_HASH_SECRET")
    vnp_url = os.getenv("VNPAY_PAYMENT_URL")
    vnp_return_url = os.getenv("FRONTEND_BASE_URL") + "/payment/return"

    
    params = {
        "vnp_Version": "2.1.0",
        "vnp_Command": "pay",
        "vnp_TmnCode": vnp_tmn_code,
        "vnp_Amount": str(int(float(amount) * 100)),  
        "vnp_CurrCode": "VND",
        "vnp_TxnRef": order_id,
        "vnp_OrderInfo": "Payment",  
        "vnp_OrderType": "other",
        "vnp_Locale": "vn",
        "vnp_CreateDate": datetime.utcnow().strftime("%Y%m%d%H%M%S"),
        "vnp_IpAddr": client_ip,
        "vnp_ReturnUrl": vnp_return_url,
    }

    
    
    

    
    filtered_params = {k: v for k, v in params.items() if v is not None and str(v).strip() != ""}

    
    sorted_params = sorted(filtered_params.items())

    
    sign_data = "&".join([f"{key}={value}" for key, value in sorted_params])

    
    secure_hash = hmac.new(
        vnp_hash_secret.encode('utf-8'),
        sign_data.encode('utf-8'),
        hashlib.sha512
    ).hexdigest()  

    
    query_string = urlencode(sorted_params)
    payment_url = f"{vnp_url}?{query_string}&vnp_SecureHash={secure_hash}"

    return payment_url, order_id

def create_vnpay_payment_url_with_order_id(user_id, course_id, amount, order_id, bank_code="NCB", client_ip="127.0.0.1"):
    """Tạo URL thanh toán VNPay với order_id có sẵn - Using Official VNPay SDK"""

    # Get configuration from environment variables
    vnp_tmn_code = os.getenv("VNPAY_TMN_CODE")
    vnp_hash_secret = os.getenv("VNPAY_HASH_SECRET")
    vnp_url = os.getenv("VNPAY_PAYMENT_URL")
    vnp_return_url = os.getenv("FRONTEND_BASE_URL") + "/payment/return"
    vnp_api_url = os.getenv("VNPAY_API_URL")


    
    vnpay = Vnpay(vnp_tmn_code, vnp_hash_secret, vnp_return_url, vnp_url, vnp_api_url)

    
    request_data = {
        "vnp_Version": "2.1.0",
        "vnp_Command": "pay",
        "vnp_TmnCode": vnp_tmn_code,
        "vnp_Amount": str(int(float(amount) * 100)),  
        "vnp_CurrCode": "VND",
        "vnp_TxnRef": order_id,
        "vnp_OrderInfo": f"Payment for course {course_id} user {user_id}",
        "vnp_OrderType": "other",
        "vnp_Locale": "vn",
        "vnp_CreateDate": datetime.now().strftime("%Y%m%d%H%M%S"),
        "vnp_IpAddr": client_ip,
        "vnp_ReturnUrl": vnp_return_url,
    }

    
    if bank_code and bank_code.strip():
        request_data["vnp_BankCode"] = bank_code

    payment_url = vnpay.get_payment_url(request_data)

    return payment_url, order_id

def verify_vnpay_signature(params):
    """Xác thực chữ ký VNPay - Fixed to match signature generation"""
    vnp_hash_secret = "H5Q37GV5CM5MDPJNI7AE5LDUTQS607QB"  
    vnp_secure_hash = params.pop("vnp_SecureHash", None)

    if not vnp_secure_hash:
        return False


    filtered_params = {}
    for key, value in params.items():
        if value is not None and str(value).strip():
            filtered_params[key] = str(value).strip()


    sorted_items = sorted(filtered_params.items())

    sign_data = "&".join([f"{key}={value}" for key, value in sorted_items])
    
    check_hash = hmac.new(
        vnp_hash_secret.encode('utf-8'),
        sign_data.encode('utf-8'),
        hashlib.sha512
    ).hexdigest()


    is_valid = check_hash.lower() == vnp_secure_hash.lower()

    return is_valid

def process_vnpay_ipn(params):

    vnp_response_code = params.get("vnp_ResponseCode")
    vnp_transaction_status = params.get("vnp_TransactionStatus")
    vnp_txn_ref = params.get("vnp_TxnRef")
    vnp_order_info = params.get("vnp_OrderInfo", "")

    if not vnp_txn_ref:
        return {"RspCode": "02", "Message": "Missing order_id"}

    if vnp_response_code == "00" and vnp_transaction_status == "00":
        success, message = update_enrollment_payment_status_by_order_id(
            vnp_txn_ref, payment_success=True
        )

        if success:
            return {"RspCode": "00", "Message": "Confirm Success"}
        else:
            return {"RspCode": "02", "Message": f"Update failed: {message}"}
    else:
        update_enrollment_payment_status_by_order_id(
            vnp_txn_ref, payment_success=False
        )
        return {"RspCode": "00", "Message": "Payment failed but confirmed"}


def create_momo_payment_request(user_id, course_id, amount):
    """Tạo payment request với MoMo"""
    import requests

    order_id = generate_order_id()

    # Get configuration from environment variables
    partner_code = os.getenv("MOMO_PARTNER_CODE")
    access_key = os.getenv("MOMO_ACCESS_KEY")
    secret_key = os.getenv("MOMO_SECRET_KEY")
    endpoint = os.getenv("MOMO_ENDPOINT")
    return_url = os.getenv("FRONTEND_BASE_URL") + "/payment/return"
    ipn_url = os.getenv("BACK_END_URL") + "/payment/momo/ipn"


    request_data = {
        "partnerCode": partner_code,
        "partnerName": "Test",
        "storeId": "MomoTestStore",
        "requestId": order_id,
        "amount": int(amount),
        "orderId": order_id,
        "orderInfo": f"Thanh toan khoa hoc {course_id} - User {user_id}",
        "redirectUrl": return_url,
        "ipnUrl": ipn_url,
        "lang": "vi",
        "extraData": "",
        "requestType": "captureWallet",  
        "signature": ""
    }

    
    raw_signature = f"accessKey={access_key}&amount={request_data['amount']}&extraData={request_data['extraData']}&ipnUrl={ipn_url}&orderId={order_id}&orderInfo={request_data['orderInfo']}&partnerCode={partner_code}&redirectUrl={return_url}&requestId={order_id}&requestType={request_data['requestType']}"

    signature = hmac.new(
        secret_key.encode('utf-8'),
        raw_signature.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

    request_data["signature"] = signature


    try:
        response = requests.post(endpoint, json=request_data, timeout=30)
        response_data = response.json()


        if response_data.get("resultCode") == 0:
            return {
                "payUrl": response_data.get("payUrl"),
                "orderId": order_id,
                "message": "MoMo payment URL created successfully"
            }
        else:
            return {
                "payUrl": None,
                "orderId": order_id,
                "message": f"MoMo error: {response_data.get('message', 'Unknown error')}"
            }

    except requests.exceptions.RequestException as e:
        return {
            "payUrl": None,
            "orderId": order_id,
            "message": f"MoMo request failed: {str(e)}"
        }
    except Exception as e:
        return {
            "payUrl": None,
            "orderId": order_id,
            "message": f"MoMo error: {str(e)}"
        }

def create_momo_payment_request_with_order_id(user_id, course_id, amount, order_id):
    """Tạo payment request với MoMo sử dụng order_id có sẵn"""
    import requests

    # Get configuration from environment variables
    partner_code = os.getenv("MOMO_PARTNER_CODE")
    access_key = os.getenv("MOMO_ACCESS_KEY")
    secret_key = os.getenv("MOMO_SECRET_KEY")
    endpoint = os.getenv("MOMO_ENDPOINT")
    return_url = os.getenv("FRONTEND_BASE_URL") + "/payment/return"
    ipn_url = os.getenv("BACK_END_URL") + "/payment/momo/ipn"

    # Kiểm tra cấu hình MoMo
    if not partner_code or not access_key or not secret_key or not endpoint:
        return {
            "payUrl": None,
            "orderId": order_id,
            "message": "MoMo configuration is not set up properly"
        }

    
    request_data = {
        "partnerCode": partner_code,
        "partnerName": "Test",
        "storeId": "MomoTestStore",
        "requestId": order_id,  
        "amount": int(amount),
        "orderId": order_id,    
        "orderInfo": f"Thanh toan khoa hoc {course_id} User {user_id}",
        "redirectUrl": return_url,
        "ipnUrl": ipn_url,
        "lang": "vi",
        "extraData": "",
        "requestType": "captureWallet",  
        "signature": ""
    }

    
    raw_signature = f"accessKey={access_key}&amount={request_data['amount']}&extraData={request_data['extraData']}&ipnUrl={ipn_url}&orderId={order_id}&orderInfo={request_data['orderInfo']}&partnerCode={partner_code}&redirectUrl={return_url}&requestId={order_id}&requestType={request_data['requestType']}"

    signature = hmac.new(
        secret_key.encode('utf-8'),
        raw_signature.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

    request_data["signature"] = signature


    try:
        response = requests.post(endpoint, json=request_data, timeout=30)
        response_data = response.json()


        if response_data.get("resultCode") == 0:
            return {
                "payUrl": response_data.get("payUrl"),
                "orderId": order_id,  
                "message": "MoMo payment URL created successfully"
            }
        else:
            return {
                "payUrl": None,
                "orderId": order_id,
                "message": f"MoMo error: {response_data.get('message', 'Unknown error')}"
            }

    except requests.exceptions.RequestException as e:
        return {
            "payUrl": None,
            "orderId": order_id,
            "message": f"MoMo request failed: {str(e)}"
        }
    except Exception as e:
        return {
            "payUrl": None,
            "orderId": order_id,
            "message": f"MoMo error: {str(e)}"
        }

def verify_momo_signature(params):
    """Xác thực chữ ký MoMo"""
    secret_key = "K951B6PE1waDMi640xX08PD3vg6EkVlz"  

    
    received_signature = params.get("signature", "")
    if not received_signature:
        return False

    
    access_key = "F8BBA842ECF85"
    amount = params.get("amount", "")
    extra_data = params.get("extraData", "")
    message = params.get("message", "")
    order_id = params.get("orderId", "")
    order_info = params.get("orderInfo", "")
    order_type = params.get("orderType", "")
    partner_code = params.get("partnerCode", "")
    pay_type = params.get("payType", "")
    request_id = params.get("requestId", "")
    response_time = params.get("responseTime", "")
    result_code = params.get("resultCode", "")
    trans_id = params.get("transId", "")

    
    raw_signature = f"accessKey={access_key}&amount={amount}&extraData={extra_data}&message={message}&orderId={order_id}&orderInfo={order_info}&orderType={order_type}&partnerCode={partner_code}&payType={pay_type}&requestId={request_id}&responseTime={response_time}&resultCode={result_code}&transId={trans_id}"

    
    calculated_signature = hmac.new(
        secret_key.encode('utf-8'),
        raw_signature.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

    return calculated_signature == received_signature

def process_momo_ipn(params):
    """Xử lý IPN từ MoMo"""

    
    if not verify_momo_signature(params):
        return {"resultCode": 97, "message": "Invalid signature"}

    
    result_code = params.get("resultCode")
    order_id = params.get("orderId")
    order_info = params.get("orderInfo", "")

    
    if not order_id:
        return {"resultCode": 2, "message": "Missing order_id"}

    
    if result_code == 0:
        success, message = update_enrollment_payment_status_by_order_id(
            order_id, payment_success=True
        )

        if success:
            return {"resultCode": 0, "message": "Confirm Success"}
        else:
            return {"resultCode": 2, "message": f"Update failed: {message}"}
    else:
        update_enrollment_payment_status_by_order_id(
            order_id, payment_success=False
        )
        return {"resultCode": 0, "message": "Payment failed but confirmed"}
