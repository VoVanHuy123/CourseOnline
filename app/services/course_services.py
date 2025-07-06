from app.models.course import Course
def get_courses():
    return Course.query.all()
