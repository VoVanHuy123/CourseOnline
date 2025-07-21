from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from app.models.user import User,UserRole,Student,Teacher,Gender # và các model khác
from app.models.course import Category,Course,Chapter,Lesson,LessonComment
from app.extensions import db
from flask_admin.contrib.sqla import ModelView
from flask_admin import Admin, expose,BaseView,AdminIndexView
from wtforms.fields import SelectField

class StudentAdmin(ModelView):
    column_exclude_list = ['password']
    form_overrides = {
        'role': SelectField,
        'gender': SelectField
    }

    form_args = {
    'gender': {
        'choices': [(gender.name, gender.value) for gender in Gender]
    },
    'role': {
        'choices': [(role.name, role.value) for role in UserRole]
    }
}
class TeacherAdmin(ModelView):
    column_exclude_list = ['password']
    form_overrides = {
        'role': SelectField
    }

    form_args = {
    'role': {
        'choices': [(role.name, role.value) for role in UserRole]
    }
}
class CourseAdmin(ModelView):
    column_list = ['id', 'title', 'price', 'teacher_id']
def init_admin(app):
    admin = Admin(app, name="Admin Panel", template_mode="bootstrap4",index_view=AdminIndexView())
    admin.add_view(StudentAdmin(Student, db.session))
    admin.add_view(TeacherAdmin(Teacher, db.session))
    admin.add_view(ModelView(Category, db.session))
    # admin.add_view(ModelView(Course, db.session))
    # admin.add_view(CourseAdmin(Course, db.session)) # dòng dây lỗi
    admin.add_view(ModelView(Chapter, db.session))
    admin.add_view(ModelView(Lesson, db.session))
    admin.add_view(ModelView(LessonComment, db.session))