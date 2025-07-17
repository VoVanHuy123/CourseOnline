from app.models.course import CourseReview
from app.extensions import db

def get_course_reviews_parent(course_id):
    course_reviews = CourseReview.query.filter_by(course_id=course_id).all()
    return course_reviews
def create_course_review(**kwargs):
    course_review = CourseReview(**kwargs)
    db.session.add(course_review)
    db.session.commit()
    return course_review
def get_course_review_by_id(id):
    course_review = CourseReview.query.get_or_404(id)
    return course_review
def update_course_review(review, **kwargs):
    for key, value in kwargs.items():
        setattr(review, key, value)
    db.session.commit()
    return review
def delete_course_review(review):
    db.session.delete(review)
    db.session.commit()