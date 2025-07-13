import random
from app import create_app
from app.extensions import db
from app.models.course import Course, Chapter, Lesson, Type
from app.models.user import User, UserRole

app = create_app()
app.app_context().push()

def seed():
    # Xóa dữ liệu cũ (nếu muốn)
    Lesson.query.delete()
    Chapter.query.delete()
    Course.query.delete()
    db.session.commit()

    # Tạo giáo viên mẫu
    teacher = User(
        username="teacher1",
        password="123456",  # Nên hash nếu dùng thực tế
        first_name="Nguyen",
        last_name="Van A",
        email="teacher1@example.com",
        role=UserRole.TEACHER
    )
    db.session.add(teacher)
    db.session.commit()

    # Tạo khóa học tuần tự
    course = Course(
        title="Khóa học Python cơ bản",
        description="Khóa học Python cho người mới bắt đầu",
        price=0,
        teacher_id=teacher.id,
        is_sequential=True,
        is_public=True
    )
    db.session.add(course)
    db.session.commit()

    # Tạo 5 chương, mỗi chương có 2-6 bài học ngẫu nhiên
    for i in range(1, 6):
        chapter = Chapter(
            title=f"Chương {i}",
            description=f"Nội dung chương {i}",
            course_id=course.id
        )
        db.session.add(chapter)
        db.session.commit()

        num_lessons = random.randint(2, 6)
        for j in range(1, num_lessons + 1):
            lesson = Lesson(
                title=f"Bài học {j} của chương {i}",
                description=f"Nội dung bài học {j} chương {i}",
                type=random.choice([Type.TEXT, Type.VIDEO, Type.FILE]),
                content_url=f"https://example.com/lesson_{i}_{j}",
                order=j,
                is_locked=True if course.is_sequential and j > 1 else False,
                is_published=True,
                chapter_id=chapter.id
            )
            db.session.add(lesson)
        db.session.commit()

    print("Đã seed dữ liệu mẫu thành công!")

if __name__ == "__main__":
    seed()