from app.models.course import LessonComment
from app.extensions import db


def get_lesson_comments(lesson_id):
    return LessonComment.query.filter_by(lesson_id=lesson_id, reply_to=None).all()
def create_lesson_comment(**kwargs):
    lesson_comment = LessonComment(**kwargs)
    db.session.add(lesson_comment)
    db.session.commit()
    return lesson_comment
def update_comment(comment, **kwargs):
    for key, value in kwargs.items():
        setattr(comment, key, value)
    db.session.commit()

def delete_comment(comment):
    db.session.delete(comment)
    db.session.commit()