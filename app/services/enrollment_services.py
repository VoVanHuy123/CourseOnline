from app.extensions import db
from app.models.course import Enrollment, Course
from app.models.user import User
from sqlalchemy import and_

def get_enrollment_by_user_and_course(user_id, course_id):
    """Lấy enrollment theo user_id và course_id"""
    return Enrollment.query.filter_by(user_id=user_id, course_id=course_id).first()

def get_enrollment_by_order_id(order_id):
    """Lấy enrollment theo order_id"""
    return Enrollment.query.filter_by(order_id=order_id).first()

def create_enrollment(user_id, course_id, order_id=None):
    """Tạo enrollment mới với order_id - Cho phép thanh toán lại nếu chưa thanh toán"""
    
    existing_enrollment = get_enrollment_by_user_and_course(user_id, course_id)
    if existing_enrollment:
        
        if existing_enrollment.status == "active":
            return None, "Bạn đã đăng ký và thanh toán khóa học này rồi"

        
        print(f"Enrollment Debug - Found existing enrollment with status: {existing_enrollment.status}")
        print(f"Enrollment Debug - Allowing re-payment with new order_id: {order_id}")

        
        existing_enrollment.order_id = order_id
        existing_enrollment.status = "pending_payment"  
        existing_enrollment.payment_status = False      

        try:
            db.session.commit()
            print(f"Enrollment Debug - Updated existing enrollment with new order_id")
            existing_enrollment._is_existing = True
            return existing_enrollment, None
        except Exception as e:
            db.session.rollback()
            return None, f"Lỗi cập nhật enrollment: {str(e)}"

    
    course = Course.query.get(course_id)
    if not course:
        return None, "Không tìm thấy khóa học"

    if not course.is_public:
        return None, "Khóa học chưa được công khai"

    
    enrollment = Enrollment(
        user_id=user_id,
        course_id=course_id,
        progress=0.0,
        status="pending_payment",  
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

    old_status = enrollment.status
    old_payment_status = enrollment.payment_status

    
    if payment_success:
        enrollment.status = "active"  
        enrollment.payment_status = True
    else:
        enrollment.status = "payment_failed"  
        enrollment.payment_status = False

    print(f"Enrollment Debug - Updating from status={old_status} to {enrollment.status}, payment_status={old_payment_status} to {enrollment.payment_status}")

    try:
        db.session.commit()
        print(f"Enrollment Debug - Successfully committed changes to database")
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

    old_status = enrollment.status
    old_payment_status = enrollment.payment_status

    if payment_success:
        enrollment.status = "active"
        enrollment.payment_status = True
    else:
        enrollment.payment_status = False

    print(f"Enrollment Debug - Updating from status={old_status} to {enrollment.status}, payment_status={old_payment_status} to {enrollment.payment_status}")

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
    """Lấy danh sách enrollment active của user"""
    return Enrollment.query.filter_by(user_id=user_id, status="active").all()

def check_user_access_to_course(user_id, course_id):
    """Kiểm tra user có quyền truy cập khóa học không"""
    enrollment = get_enrollment_by_user_and_course(user_id, course_id)
    if not enrollment:
        return False, "Bạn chưa đăng ký khóa học này"

    
    if enrollment.status != "active":
        return False, "Bạn cần thanh toán để truy cập khóa học"

    return True, "Có quyền truy cập"
