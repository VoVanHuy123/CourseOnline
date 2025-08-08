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
        self.smtp_username = os.getenv('SMTP_USERNAME', '')
        self.smtp_password = os.getenv('SMTP_PASSWORD', '')
        self.from_email = os.getenv('FROM_EMAIL', self.smtp_username)
        self.frontend_base_url = os.getenv('FRONTEND_BASE_URL', 'http://localhost:3000')

        
    def send_payment_invoice_email(self, user_email: str, user_name: str,
                                 course_data: Dict[str, Any], enrollment_data: Dict[str, Any]) -> bool:
        """
        Gửi email hóa đơn thanh toán khóa học

        Args:
            user_email: Email người nhận
            user_name: Tên người nhận
            course_data: Thông tin khóa học (id, title, price, description)
            enrollment_data: Thông tin enrollment (order_id, payment_date)

        Returns:
            bool: True nếu gửi thành công, False nếu thất bại
        """
        try:
            # Tạo subject với emoji và thông tin rõ ràng
            course_title = course_data.get('title', 'N/A')
            subject = f"✅ Thanh toán thành công - {course_title} | CourseOnline"

            # Tạo HTML content và plain text version
            html_content = self._create_invoice_html_template(
                user_name=user_name,
                course_data=course_data,
                enrollment_data=enrollment_data
            )

            plain_text_content = self._create_invoice_plain_text_template(
                user_name=user_name,
                course_data=course_data,
                enrollment_data=enrollment_data
            )

            # Gửi email với cả HTML và plain text
            success = self._send_email(
                to_email=user_email,
                subject=subject,
                html_content=html_content,
                plain_text_content=plain_text_content
            )

            if success:
                logger.info(f"Invoice email sent successfully to {user_email} for order {enrollment_data.get('order_id')}")
            else:
                logger.error(f"Failed to send invoice email to {user_email} for order {enrollment_data.get('order_id')}")

            return success

        except Exception as e:
            logger.error(f"Error sending invoice email to {user_email}: {str(e)}")
            return False
    
    def _send_email(self, to_email: str, subject: str, html_content: str, plain_text_content: Optional[str] = None) -> bool:
        """
        Gửi email qua SMTP với hỗ trợ cả HTML và plain text
        """
        try:
            # Tạo message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_email
            msg['To'] = to_email

            # Add plain text version if provided
            if plain_text_content:
                text_part = MIMEText(plain_text_content, 'plain', 'utf-8')
                msg.attach(text_part)

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
                                    enrollment_data: Dict[str, Any]) -> str:
        """
        Tạo HTML template cho email hóa đơn
        """
        # Format payment date
        payment_date = enrollment_data.get('payment_date', datetime.now())
        if isinstance(payment_date, str):
            try:
                payment_date = datetime.fromisoformat(payment_date.replace('Z', '+00:00'))
            except:
                payment_date = datetime.now()

        formatted_date = payment_date.strftime("%d/%m/%Y %H:%M:%S")

        # Format amount (from course price)
        amount = course_data.get('price', 0)
        formatted_amount = f"{amount:,.0f} VNĐ"

        # Course link
        course_link = f"{self.frontend_base_url}/courses/{course_data.get('id')}/lessons"

        payment_method = "Thanh toán trực tuyến"
        
        template_str = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hóa đơn thanh toán khóa học - CourseOnline</title>
    <!--[if mso]>
    <noscript>
        <xml>
            <o:OfficeDocumentSettings>
                <o:PixelsPerInch>96</o:PixelsPerInch>
            </o:OfficeDocumentSettings>
        </xml>
    </noscript>
    <![endif]-->
    <style>
        /* Reset styles for better email client compatibility */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            color: #2c3e50;
            background-color: #f8fafc;
            margin: 0;
            padding: 0;
            width: 100% !important;
            min-width: 100%;
            -webkit-text-size-adjust: 100%;
            -ms-text-size-adjust: 100%;
        }

        table {
            border-collapse: collapse;
            mso-table-lspace: 0pt;
            mso-table-rspace: 0pt;
        }

        .email-wrapper {
            width: 100%;
            background-color: #f8fafc;
            padding: 20px 0;
        }

        .email-container {
            max-width: 600px;
            margin: 0 auto;
            background-color: #ffffff;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }

        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-align: center;
            padding: 40px 30px;
            position: relative;
        }

        .header::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grain" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="25" cy="25" r="1" fill="white" opacity="0.1"/><circle cx="75" cy="75" r="1" fill="white" opacity="0.1"/><circle cx="50" cy="10" r="0.5" fill="white" opacity="0.1"/><circle cx="10" cy="60" r="0.5" fill="white" opacity="0.1"/><circle cx="90" cy="40" r="0.5" fill="white" opacity="0.1"/></pattern></defs><rect width="100" height="100" fill="url(%23grain)"/></svg>');
        }

        .header-content {
            position: relative;
            z-index: 1;
        }

        .logo {
            font-size: 32px;
            font-weight: 800;
            margin-bottom: 8px;
            letter-spacing: -0.5px;
        }

        .header-subtitle {
            font-size: 16px;
            opacity: 0.9;
            font-weight: 400;
        }

        .content {
            padding: 40px 30px;
        }

        .greeting {
            font-size: 18px;
            margin-bottom: 20px;
            color: #2c3e50;
        }

        .success-badge {
            display: inline-flex;
            align-items: center;
            background: linear-gradient(135deg, #10b981, #059669);
            color: white;
            padding: 12px 20px;
            border-radius: 25px;
            font-weight: 600;
            margin-bottom: 30px;
            font-size: 14px;
        }

        .course-card {
            background: linear-gradient(135deg, #f0f9ff, #e0f2fe);
            border: 1px solid #0ea5e9;
            border-radius: 12px;
            padding: 25px;
            margin-bottom: 30px;
            position: relative;
            overflow: hidden;
        }

        .course-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 4px;
            height: 100%;
            background: linear-gradient(to bottom, #0ea5e9, #0284c7);
        }

        .course-title {
            font-size: 22px;
            font-weight: 700;
            color: #0c4a6e;
            margin-bottom: 12px;
            line-height: 1.3;
        }

        .course-description {
            color: #475569;
            font-size: 15px;
            line-height: 1.5;
        }

        .invoice-details {
            background-color: #f8fafc;
            border-radius: 12px;
            padding: 25px;
            margin-bottom: 30px;
        }

        .invoice-title {
            font-size: 18px;
            font-weight: 600;
            color: #1e293b;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
        }

        .detail-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px 0;
            border-bottom: 1px solid #e2e8f0;
        }

        .detail-row:last-child {
            border-bottom: none;
            font-weight: 600;
            font-size: 16px;
        }

        .detail-label {
            color: #64748b;
            font-weight: 500;
        }

        .detail-value {
            color: #1e293b;
            font-weight: 600;
        }

        .amount-highlight {
            background: linear-gradient(135deg, #10b981, #059669);
            color: white;
            padding: 20px;
            border-radius: 12px;
            text-align: center;
            margin: 30px 0;
            box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3);
        }

        .amount-text {
            font-size: 14px;
            opacity: 0.9;
            margin-bottom: 5px;
        }

        .amount-value {
            font-size: 28px;
            font-weight: 800;
            letter-spacing: -0.5px;
        }

        .cta-section {
            text-align: center;
            margin: 40px 0;
        }

        .cta-button {
            display: inline-block;
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white !important;
            text-decoration: none;
            padding: 16px 32px;
            border-radius: 8px;
            font-weight: 600;
            font-size: 16px;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        }

        .cta-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
        }

        .footer {
            background-color: #f1f5f9;
            padding: 30px;
            text-align: center;
            border-top: 1px solid #e2e8f0;
        }

        .footer-text {
            color: #64748b;
            font-size: 14px;
            line-height: 1.6;
            margin-bottom: 15px;
        }

        .company-info {
            color: #94a3b8;
            font-size: 12px;
            margin-top: 20px;
        }

        /* Mobile responsiveness */
        @media only screen and (max-width: 600px) {
            .email-wrapper {
                padding: 10px;
            }

            .email-container {
                border-radius: 8px;
            }

            .header {
                padding: 30px 20px;
            }

            .content {
                padding: 30px 20px;
            }

            .logo {
                font-size: 28px;
            }

            .course-title {
                font-size: 20px;
            }

            .detail-row {
                flex-direction: column;
                align-items: flex-start;
                gap: 5px;
            }

            .cta-button {
                display: block;
                margin: 0 auto;
            }

            .amount-value {
                font-size: 24px;
            }
        }

        /* Dark mode support */
        @media (prefers-color-scheme: dark) {
            .email-container {
                background-color: #1e293b;
            }

            .content {
                color: #e2e8f0;
            }

            .greeting {
                color: #f1f5f9;
            }

            .invoice-details {
                background-color: #334155;
            }

            .detail-label {
                color: #94a3b8;
            }

            .detail-value {
                color: #f1f5f9;
            }
        }
    </style>
</head>
<body>
    <div class="email-wrapper">
        <div class="email-container">
            <!-- Header Section -->
            <div class="header">
                <div class="header-content">
                    <div class="logo">📚 CourseOnline</div>
                    <div class="header-subtitle">Nền tảng học trực tuyến hàng đầu</div>
                </div>
            </div>

            <!-- Main Content -->
            <div class="content">
                <!-- Success Badge -->
                <div class="success-badge">
                    ✅ Thanh toán thành công
                </div>

                <!-- Greeting -->
                <div class="greeting">
                    Xin chào <strong>{{ user_name }}</strong>,
                </div>

                <p style="color: #475569; font-size: 16px; line-height: 1.6; margin-bottom: 30px;">
                    Chúc mừng! Bạn đã thanh toán thành công và chính thức trở thành học viên của khóa học.
                    Chúng tôi rất vui mừng chào đón bạn tham gia cộng đồng học tập của CourseOnline.
                </p>

                <!-- Course Information Card -->
                <div class="course-card">
                    <div class="course-title">{{ course_title }}</div>
                    <div class="course-description">{{ course_description }}</div>
                </div>

                <!-- Invoice Details -->
                <div class="invoice-details">
                    <div class="invoice-title">
                        📋 Chi tiết thanh toán
                    </div>

                    <div class="detail-row">
                        <span class="detail-label">Mã đơn hàng</span>
                        <span class="detail-value">{{ order_id }}</span>
                    </div>

                    <div class="detail-row">
                        <span class="detail-label">Phương thức thanh toán</span>
                        <span class="detail-value">{{ payment_method }}</span>
                    </div>

                    <div class="detail-row">
                        <span class="detail-label">Ngày thanh toán</span>
                        <span class="detail-value">{{ payment_date }}</span>
                    </div>

                    <div class="detail-row">
                        <span class="detail-label">Trạng thái</span>
                        <span class="detail-value" style="color: #10b981;">✅ Đã thanh toán</span>
                    </div>

                    <div class="detail-row">
                        <span class="detail-label">Tổng tiền</span>
                        <span class="detail-value" style="font-size: 18px; color: #10b981;">{{ amount }}</span>
                    </div>
                </div>

                <!-- Call to Action -->
                <div class="cta-section">
                    <a href="{{ course_link }}" class="cta-button">
                        🚀 Bắt đầu học ngay
                    </a>
                    <p style="color: #64748b; font-size: 14px; margin-top: 15px;">
                        Nhấn vào nút trên để truy cập khóa học của bạn
                    </p>
                </div>

                <!-- Additional Information -->
                <div style="background-color: #fef3c7; border: 1px solid #f59e0b; border-radius: 8px; padding: 20px; margin-top: 30px;">
                    <h3 style="color: #92400e; margin: 0 0 10px 0; font-size: 16px;">💡 Lưu ý quan trọng:</h3>
                    <ul style="color: #92400e; margin: 0; padding-left: 20px; font-size: 14px;">
                        <li>Bạn có thể truy cập khóa học bất cứ lúc nào sau khi thanh toán</li>
                        <li>Tài khoản của bạn đã được kích hoạt và sẵn sàng sử dụng</li>
                        <li>Hãy lưu email này để làm bằng chứng thanh toán</li>
                    </ul>
                </div>
            </div>

            <!-- Footer -->
            <div class="footer">
                <div class="footer-text">
                    <strong>Cần hỗ trợ?</strong><br>
                    Nếu bạn có bất kỳ câu hỏi nào về khóa học hoặc cần hỗ trợ kỹ thuật,
                    đừng ngần ngại liên hệ với đội ngũ hỗ trợ của chúng tôi.
                </div>

                <div class="footer-text">
                    Chúc bạn có những trải nghiệm học tập tuyệt vời! 🎯
                </div>

                <div class="company-info">
                    <strong>CourseOnline</strong> - Nền tảng học trực tuyến hàng đầu<br>
                    Email này được gửi tự động, vui lòng không trả lời trực tiếp.
                </div>
            </div>
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
            order_id=enrollment_data.get('order_id', 'N/A'),
            payment_method=payment_method,
            payment_date=formatted_date,
            amount=formatted_amount,
            course_link=course_link
        )

    def _create_invoice_plain_text_template(self, user_name: str, course_data: Dict[str, Any],
                                          enrollment_data: Dict[str, Any]) -> str:
        """
        Tạo plain text template cho email hóa đơn (fallback cho email clients không hỗ trợ HTML)
        """
        # Format payment date
        payment_date = enrollment_data.get('payment_date', datetime.now())
        if isinstance(payment_date, str):
            try:
                payment_date = datetime.fromisoformat(payment_date.replace('Z', '+00:00'))
            except:
                payment_date = datetime.now()

        formatted_date = payment_date.strftime("%d/%m/%Y %H:%M:%S")

        # Format amount
        amount = course_data.get('price', 0)
        formatted_amount = f"{amount:,.0f} VNĐ"

        # Course link
        course_link = f"{self.frontend_base_url}/courses/{course_data.get('id')}/lessons"

        plain_text = f"""
COURSEONLINE - HÓA ĐƠN THANH TOÁN
=====================================

✅ THANH TOÁN THÀNH CÔNG

Xin chào {user_name},

Chúc mừng! Bạn đã thanh toán thành công và chính thức trở thành học viên của khóa học.
Chúng tôi rất vui mừng chào đón bạn tham gia cộng đồng học tập của CourseOnline.

THÔNG TIN KHÓA HỌC:
-------------------
Tên khóa học: {course_data.get('title', 'N/A')}
Mô tả: {course_data.get('description', '')}

CHI TIẾT THANH TOÁN:
-------------------
Mã đơn hàng: {enrollment_data.get('order_id', 'N/A')}
Phương thức thanh toán: Thanh toán trực tuyến
Ngày thanh toán: {formatted_date}
Trạng thái: ✅ Đã thanh toán
Tổng tiền: {formatted_amount}

TRUY CẬP KHÓA HỌC:
-----------------
Bạn có thể bắt đầu học ngay bằng cách truy cập:
{course_link}

LƯU Ý QUAN TRỌNG:
----------------
• Bạn có thể truy cập khóa học bất cứ lúc nào sau khi thanh toán
• Tài khoản của bạn đã được kích hoạt và sẵn sàng sử dụng
• Hãy lưu email này để làm bằng chứng thanh toán

HỖ TRỢ:
-------
Nếu bạn có bất kỳ câu hỏi nào về khóa học hoặc cần hỗ trợ kỹ thuật,
đừng ngần ngại liên hệ với đội ngũ hỗ trợ của chúng tôi.

Chúc bạn có những trải nghiệm học tập tuyệt vời! 🎯

---
CourseOnline - Nền tảng học trực tuyến hàng đầu
Email này được gửi tự động, vui lòng không trả lời trực tiếp.
        """

        return plain_text.strip()

# Singleton instance
email_service = EmailService()
