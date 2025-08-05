# Email Service for Payment Invoice Notifications

## Overview
Hệ thống email tự động gửi hóa đơn thanh toán khóa học sau khi người dùng thanh toán thành công.

## Features

### 🎯 Core Features
- ✅ **Automatic Email Sending**: Tự động gửi email sau khi payment status được cập nhật thành công
- ✅ **Beautiful HTML Templates**: Email template responsive và đẹp mắt
- ✅ **Payment Method Tracking**: Lưu trữ và hiển thị phương thức thanh toán (VNPay/MoMo)
- ✅ **Error Handling**: Xử lý lỗi không ảnh hưởng đến luồng thanh toán chính
- ✅ **Comprehensive Logging**: Ghi log chi tiết cho việc theo dõi
- ✅ **Duplicate Prevention**: Đảm bảo email chỉ được gửi một lần cho mỗi thanh toán

### 📧 Email Content
- **Subject**: "Hóa đơn thanh toán khóa học - [Tên khóa học]"
- **Content includes**:
  - Thông tin khóa học (tên, mô tả)
  - Số tiền đã thanh toán
  - Phương thức thanh toán (VNPay/MoMo)
  - Order ID
  - Ngày thanh toán
  - Link truy cập khóa học
  - Responsive design cho mobile/desktop

## Architecture

### 🏗️ Components
1. **EmailService** (`app/services/email_services.py`)
   - SMTP email sending
   - HTML template generation
   - Error handling and logging

2. **Existing Models Integration**
   - Uses only existing models: Enrollment, Course, User
   - No additional database tables required
   - Leverages order_id and timestamps from Enrollment

3. **Email API Endpoints** (`app/routes/email/email.py`)
   - Manual email sending for testing
   - Resend functionality for admins
   - Test email functionality

4. **Integration Points**
   - VNPay IPN handler
   - MoMo IPN handler
   - Enrollment services

### 🔄 Flow Diagram
```
Payment Gateway (VNPay/MoMo)
    ↓ IPN/Callback
Payment Service
    ↓ Update Enrollment (payment_status = True)
Enrollment Service
    ↓ Check payment_status change (False → True)
    ↓ Send Email (if first time, prevent duplicates)
Email Service
    ↓ Generate HTML template
    ↓ Send via SMTP
User receives invoice email
```

## Configuration

### 📧 Email Settings (.env)
```bash
# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
FROM_EMAIL=your_email@gmail.com

# Frontend URL for course links
FRONTEND_BASE_URL=http://localhost:3000
```

### 🔐 Gmail Setup
1. Enable 2-factor authentication
2. Generate App Password: https://myaccount.google.com/apppasswords
3. Use App Password as SMTP_PASSWORD (not regular password)

### 📧 Other Email Providers
- **Outlook**: smtp-mail.outlook.com:587
- **Yahoo**: smtp.mail.yahoo.com:587
- **Custom SMTP**: Use your provider's settings

## API Endpoints

### 🔧 Admin APIs

#### Send Invoice Email
```http
POST /email/invoice/send
Authorization: Bearer <admin_jwt_token>
Content-Type: application/json

{
    "enrollment_id": 123,
    "force_resend": false
}
```

#### Resend Invoice Email
```http
POST /email/invoice/resend/{enrollment_id}
Authorization: Bearer <admin_jwt_token>
```

#### Test Email
```http
POST /email/test
Authorization: Bearer <admin_jwt_token>
Content-Type: application/json

{
    "to_email": "test@example.com",
    "subject": "Test Email",
    "content": "This is a test email",
    "is_html": false
}
```

## Database Schema

### Using Existing Models Only
- **Enrollment**: Contains order_id, payment_status, created_day, updated_day
- **Course**: Contains title, description, price
- **User**: Contains email, full_name, username

No additional database tables required! The system leverages existing data structure.

## Testing

### 🧪 Manual Testing
1. **Setup email configuration** in .env file
2. **Test email sending**:
   ```bash
   curl -X POST http://localhost:5000/email/test \
     -H "Authorization: Bearer <admin_token>" \
     -H "Content-Type: application/json" \
     -d '{
       "to_email": "your_email@example.com",
       "subject": "Test Email",
       "content": "This is a test email",
       "is_html": false
     }'
   ```

3. **Test payment flow**:
   - Make a test payment through VNPay/MoMo
   - Check logs for email sending status
   - Verify email received in inbox

### 📊 Monitoring
- Check application logs for email sending status
- Monitor SMTP connection errors
- Track email delivery rates

## Error Handling

### 🛡️ Safeguards
- **Non-blocking**: Email errors don't affect payment processing
- **Retry logic**: Can manually resend emails via API
- **Comprehensive logging**: All email attempts are logged
- **Graceful degradation**: System continues working even if email fails

### 🔍 Common Issues
1. **SMTP Authentication Failed**
   - Check username/password
   - Verify App Password for Gmail
   - Check 2FA settings

2. **Email Not Received**
   - Check spam folder
   - Verify email address
   - Check SMTP server settings

3. **Template Rendering Errors**
   - Check course/user data completeness
   - Verify template syntax

## Security

### 🔒 Security Measures
- **Admin-only APIs**: Email management requires admin privileges
- **Input validation**: All email inputs are validated
- **SMTP encryption**: Uses TLS/SSL for email transmission
- **No sensitive data in logs**: Passwords and sensitive info are not logged

## Future Enhancements

### 🚀 Potential Improvements
- [ ] Email templates for different languages
- [ ] Email delivery status tracking
- [ ] Bulk email sending for promotions
- [ ] Email analytics and open rates
- [ ] Integration with email marketing services
- [ ] SMS notifications as backup
- [ ] Email scheduling functionality

## Support

### 📞 Troubleshooting
1. Check application logs for detailed error messages
2. Verify email configuration in .env file
3. Test SMTP connection manually
4. Use test email API to verify setup
5. Check database for PaymentHistory records

### 📝 Logs Location
- Application logs: Check console output
- Email service logs: Tagged with "EmailService"
- Payment service logs: Tagged with "PaymentService"
