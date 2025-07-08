import hashlib
from app.models.user import User,Teacher
def get_teacher(id):
    return Teacher.query.filter_by(id=id).first()