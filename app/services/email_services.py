import os
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Optional, Dict, Any
from jinja2 import Template

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_username = os.getenv('SMTP_USERNAME')
        self.smtp_password = os.getenv('SMTP_PASSWORD')
        self.from_email = os.getenv('FROM_EMAIL', self.smtp_username)
        self.frontend_base_url = os.getenv('FRONTEND_BASE_URL', 'http://localhost:3000')
        
    def send_payment_invoice_email(self, user_email: str, user_name: str, 
                                 course_data: Dict[str, Any], payment_data: Dict[str, Any]) -> bool:
        """
        Gửi email hóa đơn thanh toán khóa học
        
        Args:
            user_email: Email người nhận
            user_name: Tên người nhận
            course_data: Thông tin khóa học (id, title, price, description)
            payment_data: Thông tin thanh toán (order_id, payment_method, amount, payment_date)
        
        Returns:
            bool: True nếu gửi thành công, False nếu thất bại
        """
        try:
            # Tạo subject
            subject = f"Hóa đơn thanh toán khóa học - {course_data.get('title', 'N/A')}"
            
            # Tạo HTML content
            html_content = self._create_invoice_html_template(
                user_name=user_name,
                course_data=course_data,
                payment_data=payment_data
            )
            
            # Gửi email
            success = self._send_email(
                to_email=user_email,
                subject=subject,
                html_content=html_content
            )
            
            if success:
                logger.info(f"Invoice email sent successfully to {user_email} for order {payment_data.get('order_id')}")
            else:
                logger.error(f"Failed to send invoice email to {user_email} for order {payment_data.get('order_id')}")
                
            return success
            
        except Exception as e:
            logger.error(f"Error sending invoice email to {user_email}: {str(e)}")
            return False
    
    def _send_email(self, to_email: str, subject: str, html_content: str) -> bool:
        """
        Gửi email qua SMTP
        """
        try:
            # Tạo message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_email
            msg['To'] = to_email
            
            # Attach HTML content
            html_part = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(html_part)
            
            # Kết nối SMTP và gửi email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
                
            return True
            
        except Exception as e:
            logger.error(f"SMTP error: {str(e)}")
            return False
    
    def _create_invoice_html_template(self, user_name: str, course_data: Dict[str, Any], 
                                    payment_data: Dict[str, Any]) -> str:
        """
        Tạo HTML template cho email hóa đơn
        """
        # Format payment date
        payment_date = payment_data.get('payment_date', datetime.now())
        if isinstance(payment_date, str):
            try:
                payment_date = datetime.fromisoformat(payment_date.replace('Z', '+00:00'))
            except:
                payment_date = datetime.now()
        
        formatted_date = payment_date.strftime("%d/%m/%Y %H:%M:%S")
        
        # Format amount
        amount = payment_data.get('amount', 0)
        formatted_amount = f"{amount:,.0f} VNĐ"
        
        # Course link
        course_link = f"{self.frontend_base_url}/courses/{course_data.get('id')}/lessons"
        
        # Payment method display
        payment_method = payment_data.get('payment_method', 'N/A').upper()
        
        template_str = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hóa đơn thanh toán khóa học</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f4f4f4;
        }
        .container {
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }
        .header {
            text-align: center;
            border-bottom: 3px solid #007bff;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }
        .header h1 {
            color: #007bff;
            margin: 0;
            font-size: 28px;
        }
        .invoice-info {
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 25px;
        }
        .info-row {
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
            padding: 8px 0;
            border-bottom: 1px solid #e9ecef;
        }
        .info-row:last-child {
            border-bottom: none;
        }
        .label {
            font-weight: bold;
            color: #495057;
        }
        .value {
            color: #212529;
        }
        .course-info {
            background-color: #e3f2fd;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 25px;
        }
        .course-title {
            font-size: 20px;
            font-weight: bold;
            color: #1976d2;
            margin-bottom: 10px;
        }
        .amount-highlight {
            background-color: #28a745;
            color: white;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
            font-size: 24px;
            font-weight: bold;
            margin: 20px 0;
        }
        .cta-button {
            display: inline-block;
            background-color: #007bff;
            color: white;
            padding: 15px 30px;
            text-decoration: none;
            border-radius: 5px;
            font-weight: bold;
            text-align: center;
            margin: 20px 0;
        }
        .footer {
            text-align: center;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #e9ecef;
            color: #6c757d;
            font-size: 14px;
        }
        @media (max-width: 600px) {
            body { padding: 10px; }
            .container { padding: 20px; }
            .info-row { flex-direction: column; }
            .cta-button { display: block; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎓 HÓA ĐƠN THANH TOÁN</h1>
            <p>Cảm ơn bạn đã đăng ký khóa học!</p>
        </div>
        
        <p>Xin chào <strong>{{ user_name }}</strong>,</p>
        <p>Chúng tôi xác nhận rằng bạn đã thanh toán thành công cho khóa học. Dưới đây là thông tin chi tiết:</p>
        
        <div class="course-info">
            <div class="course-title">{{ course_title }}</div>
            <p>{{ course_description }}</p>
        </div>
        
        <div class="invoice-info">
            <div class="info-row">
                <span class="label">Mã đơn hàng:</span>
                <span class="value">{{ order_id }}</span>
            </div>
            <div class="info-row">
                <span class="label">Phương thức thanh toán:</span>
                <span class="value">{{ payment_method }}</span>
            </div>
            <div class="info-row">
                <span class="label">Ngày thanh toán:</span>
                <span class="value">{{ payment_date }}</span>
            </div>
            <div class="info-row">
                <span class="label">Trạng thái:</span>
                <span class="value" style="color: #28a745; font-weight: bold;">✅ Đã thanh toán</span>
            </div>
        </div>
        
        <div class="amount-highlight">
            Tổng tiền: {{ amount }}
        </div>
        
        <div style="text-align: center;">
            <a href="{{ course_link }}" class="cta-button">🚀 BẮT ĐẦU HỌC NGAY</a>
        </div>
        
        <div class="footer">
            <p>Nếu bạn có bất kỳ câu hỏi nào, vui lòng liên hệ với chúng tôi.</p>
            <p>Chúc bạn học tập hiệu quả! 📚</p>
            <p><em>Email này được gửi tự động, vui lòng không trả lời.</em></p>
        </div>
    </div>
</body>
</html>
        """
        
        template = Template(template_str)
        return template.render(
            user_name=user_name,
            course_title=course_data.get('title', 'N/A'),
            course_description=course_data.get('description', ''),
            order_id=payment_data.get('order_id', 'N/A'),
            payment_method=payment_method,
            payment_date=formatted_date,
            amount=formatted_amount,
            course_link=course_link
        )

# Singleton instance
email_service = EmailService()
