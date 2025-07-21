import hashlib
from app.models.user import User,Teacher
def get_teacher(id):
    return Teacher.query.filter_by(id=id).first()
def get_user_by_id(id):
    return User.query.get(id)