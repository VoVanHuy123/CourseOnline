#!/usr/bin/env python3
"""
Test script for Email Service
Kiểm tra tính năng gửi email hóa đơn thanh toán
"""

import os
import sys
from datetime import datetime

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.email_services import email_service

def test_email_service():
    """Test email service với dữ liệu mẫu"""
    
    print("🧪 Testing Email Service...")
    
    # Dữ liệu test
    user_email = "test@example.com"  # Thay bằng email thật để test
    user_name = "Nguyễn Văn Test"
    
    course_data = {
        'id': 1,
        'title': 'Khóa học lập trình Python cơ bản',
        'description': 'Học lập trình Python từ cơ bản đến nâng cao với các dự án thực tế',
        'price': 299000
    }
    
    enrollment_data = {
        'order_id': 'TEST123456',
        'payment_date': datetime.now()
    }
    
    print(f"📧 Sending test email to: {user_email}")
    print(f"📚 Course: {course_data['title']}")
    print(f"💰 Amount: {course_data['price']:,} VNĐ")
    print(f"🆔 Order ID: {enrollment_data['order_id']}")
    
    # Gửi email test
    try:
        success = email_service.send_payment_invoice_email(
            user_email=user_email,
            user_name=user_name,
            course_data=course_data,
            enrollment_data=enrollment_data
        )
        
        if success:
            print("✅ Email sent successfully!")
            print("📬 Please check your inbox (and spam folder)")
        else:
            print("❌ Failed to send email")
            print("🔧 Please check your email configuration in .env file")
            
    except Exception as e:
        print(f"💥 Error: {str(e)}")
        print("🔧 Please check your email configuration:")
        print("   - SMTP_SERVER")
        print("   - SMTP_PORT") 
        print("   - SMTP_USERNAME")
        print("   - SMTP_PASSWORD")
        print("   - FROM_EMAIL")

def check_email_config():
    """Kiểm tra cấu hình email"""
    
    print("\n🔍 Checking Email Configuration...")
    
    required_vars = [
        'SMTP_SERVER',
        'SMTP_PORT', 
        'SMTP_USERNAME',
        'SMTP_PASSWORD',
        'FROM_EMAIL'
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if value:
            if var == 'SMTP_PASSWORD':
                print(f"✅ {var}: {'*' * len(value)}")
            else:
                print(f"✅ {var}: {value}")
        else:
            print(f"❌ {var}: Not set")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n⚠️  Missing configuration: {', '.join(missing_vars)}")
        print("📝 Please add these to your .env file")
        return False
    else:
        print("\n✅ All email configuration variables are set!")
        return True

if __name__ == "__main__":
    print("🚀 Email Service Test Script")
    print("=" * 50)
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Check configuration
    config_ok = check_email_config()
    
    if config_ok:
        print("\n" + "=" * 50)
        test_email_service()
    else:
        print("\n❌ Cannot test email service without proper configuration")
        print("📖 Please refer to .env.example for setup instructions")
    
    print("\n" + "=" * 50)
    print("🏁 Test completed!")
