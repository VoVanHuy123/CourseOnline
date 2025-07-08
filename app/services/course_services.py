from app.extensions import db
from app.models.course import Course,Chapter,Lesson,Category
from app.models.user import Teacher
def get_courses():
    return Course.query.all()

def get_course_by_id(id):
    return Course.query.filter_by(id=id).first()

def get_chapter_by_id(id):
    return Chapter.query.filter_by(id=id).first()

def get_category_by_id(id):
    return Category.query.filter_by(id=id).first()

def create_course_in_db(**kwargs):
    course = Course(**kwargs)
    db.session.add(course)
    db.session.commit()
    return course

def create_chapter_in_db(**kwargs):
    chater = Chapter(
        title=kwargs["title"],
        description=kwargs["description"],
        course_id=kwargs["course_id"]
    )
    db.session.add(chater)
    db.session.commit()
    return chater
def create_lesson_in_db(**kwargs):
    lesson = Lesson(**kwargs)
    db.session.add(lesson)
    db.session.commit()
    return lesson