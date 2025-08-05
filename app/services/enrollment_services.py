from app.extensions import db
from app.models.course import Enrollment, Course, Status
from app.models.user import User
from sqlalchemy import and_
from datetime import datetime
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Set để track các enrollment đã gửi email (tránh gửi trùng lặp trong session)
_email_sent_enrollments = set()

def get_enrollment_by_user_and_course(user_id, course_id):
    """Lấy enrollment theo user_id và course_id"""
    return Enrollment.query.filter_by(user_id=user_id, course_id=course_id).first()

def get_enrollment_by_order_id(order_id):
    """Lấy enrollment theo order_id"""
    return Enrollment.query.filter_by(order_id=order_id).first()

def create_enrollment(user_id, course_id, order_id=None):
    """Tạo enrollment mới với order_id - Cho phép thanh toán lại nếu chưa thanh toán"""
    print(f"Enrollment Debug - create_enrollment called: user_id={user_id}, course_id={course_id}, order_id={order_id}")

    existing_enrollment = get_enrollment_by_user_and_course(user_id, course_id)
    if existing_enrollment:
        
        if existing_enrollment.payment_status == True:
            return None, "Bạn đã đăng ký và thanh toán khóa học này rồi"


        print(f"Enrollment Debug - Found existing enrollment with payment_status: {existing_enrollment.payment_status}")
        print(f"Enrollment Debug - Allowing re-payment with new order_id: {order_id}")


        existing_enrollment.order_id = order_id
        # Don't change status, only update payment-related fields
        existing_enrollment.payment_status = False

        try:
            db.session.commit()
            print(f"Enrollment Debug - Updated existing enrollment with new order_id")
            existing_enrollment._is_existing = True
            return existing_enrollment, None
        except Exception as e:
            db.session.rollback()
            return None, f"Lỗi cập nhật enrollment: {str(e)}"


    print(f"Enrollment Debug - Checking course {course_id}")
    course = Course.query.get(course_id)
    if not course:
        print(f"Enrollment Debug - Course {course_id} not found")
        return None, "Không tìm thấy khóa học"

    print(f"Enrollment Debug - Course {course_id} found: {course.title}, is_public={course.is_public}")
    if not course.is_public:
        print(f"Enrollment Debug - Course {course_id} is not public")
        return None, "Khóa học chưa được công khai"


    enrollment = Enrollment(
        user_id=user_id,
        course_id=course_id,
        progress=0.0,
        status=Status.UNFINISHED,
        payment_status=False,
        order_id=order_id
    )

    db.session.add(enrollment)
    db.session.commit()

    return enrollment, None

def update_enrollment_payment_status_by_order_id(order_id, payment_success=True):
    """Cập nhật trạng thái thanh toán của enrollment theo order_id"""
    print(f"Enrollment Debug - Updating payment status for order_id={order_id}, payment_success={payment_success}")

    enrollment = get_enrollment_by_order_id(order_id)
    if not enrollment:
        print(f"Enrollment Debug - No enrollment found for order_id={order_id}")
        return False, "Không tìm thấy đăng ký khóa học với order_id này"

    print(f"Enrollment Debug - Found enrollment: id={enrollment.id}, user_id={enrollment.user_id}, course_id={enrollment.course_id}, order_id={enrollment.order_id}, current_status={enrollment.status}, current_payment_status={enrollment.payment_status}")

    old_payment_status = enrollment.payment_status

    # Only update payment_status, not the general status field
    # The status field should only be updated based on learning progress
    enrollment.payment_status = payment_success

    print(f"Enrollment Debug - Updating payment_status from {old_payment_status} to {enrollment.payment_status}, status remains {enrollment.status}")

    try:
        db.session.commit()
        print(f"Enrollment Debug - Successfully committed changes to database")

        # Gửi email hóa đơn nếu thanh toán thành công và chưa gửi trước đó
        if payment_success and not old_payment_status:
            try:
                # Kiểm tra xem đã gửi email cho enrollment này chưa
                if enrollment.id not in _email_sent_enrollments:
                    send_payment_invoice_email(enrollment)
                    _email_sent_enrollments.add(enrollment.id)
                else:
                    logger.info(f"Email already sent for enrollment {enrollment.id}, skipping")
            except Exception as email_error:
                logger.error(f"Failed to send invoice email for enrollment {enrollment.id}: {str(email_error)}")
                # Không return False vì email lỗi không ảnh hưởng đến payment flow

        return True, "Cập nhật thành công"
    except Exception as e:
        print(f"Enrollment Debug - Database commit failed: {str(e)}")
        db.session.rollback()
        return False, f"Lỗi database: {str(e)}"

def update_enrollment_payment_status(user_id, course_id, payment_success=True):
    """Cập nhật trạng thái thanh toán của enrollment theo user_id và course_id (legacy function)"""
    print(f"Enrollment Debug - Legacy function called for user_id={user_id}, course_id={course_id}, payment_success={payment_success}")

    enrollment = get_enrollment_by_user_and_course(user_id, course_id)
    if not enrollment:
        print(f"Enrollment Debug - No enrollment found for user_id={user_id}, course_id={course_id}")
        return False, "Không tìm thấy đăng ký khóa học"

    print(f"Enrollment Debug - Found enrollment: id={enrollment.id}, current_status={enrollment.status}, current_payment_status={enrollment.payment_status}")

    old_payment_status = enrollment.payment_status

    # Only update payment_status, not the general status field
    enrollment.payment_status = payment_success

    print(f"Enrollment Debug - Updating payment_status from {old_payment_status} to {enrollment.payment_status}, status remains {enrollment.status}")

    try:
        db.session.commit()
        print(f"Enrollment Debug - Successfully committed changes to database")
        return True, "Cập nhật thành công"
    except Exception as e:
        print(f"Enrollment Debug - Database commit failed: {str(e)}")
        db.session.rollback()
        return False, f"Lỗi database: {str(e)}"

def get_enrollments_by_user(user_id):
    """Lấy danh sách enrollment của user"""
    return Enrollment.query.filter_by(user_id=user_id).all()

def get_active_enrollments_by_user(user_id):
    """Lấy danh sách enrollment đã thanh toán của user"""
    return Enrollment.query.filter_by(user_id=user_id, payment_status=True).all()

def check_user_access_to_course(user_id, course_id):
    """Kiểm tra user có quyền truy cập khóa học không"""
    enrollment = get_enrollment_by_user_and_course(user_id, course_id)
    if not enrollment:
        return False, "Bạn chưa đăng ký khóa học này"


    if not enrollment.payment_status:
        return False, "Bạn cần thanh toán để truy cập khóa học"

    return True, "Có quyền truy cập"

def send_payment_invoice_email(enrollment):
    """
    Gửi email hóa đơn thanh toán cho enrollment

    Args:
        enrollment: Enrollment object đã thanh toán thành công
    """
    try:
        from app.services.email_services import email_service

        # Lấy thông tin user
        user = User.query.get(enrollment.user_id)
        if not user:
            logger.error(f"User not found for enrollment {enrollment.id}")
            return False

        # Lấy thông tin course
        course = Course.query.get(enrollment.course_id)
        if not course:
            logger.error(f"Course not found for enrollment {enrollment.id}")
            return False

        # Chuẩn bị dữ liệu course
        course_data = {
            'id': course.id,
            'title': course.title,
            'description': course.description or '',
            'price': course.price
        }

        # Chuẩn bị dữ liệu enrollment (chỉ sử dụng model có sẵn)
        enrollment_data = {
            'order_id': enrollment.order_id or 'N/A',
            'payment_date': enrollment.updated_day or enrollment.created_day or datetime.now()
        }

        # Gửi email
        success = email_service.send_payment_invoice_email(
            user_email=user.email,
            user_name=user.full_name or user.username,
            course_data=course_data,
            enrollment_data=enrollment_data
        )

        if success:
            logger.info(f"Invoice email sent successfully for enrollment {enrollment.id}")
        else:
            logger.error(f"Failed to send invoice email for enrollment {enrollment.id}")

        return success

    except Exception as e:
        logger.error(f"Error in send_payment_invoice_email for enrollment {enrollment.id}: {str(e)}")
        return False
