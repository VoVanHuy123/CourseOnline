import hashlib
from app.models.user import User
# def check_login(username, password):
#     if username and password:
#         password = str(hashlib.md5((password).strip().encode('utf-8')).hexdigest())

#         return User.query.filter(User.username.__eq__(username.strip()),
#                                 User.password.__eq__(password)).first()