from app import create_app
from app.extensions import db
from flask.cli import with_appcontext
from app.services.course_services import get_courses



app = create_app()

if __name__ == '__main__':
    with app.app_context():
        # print(get_courses())
        db.create_all()
        app.run(debug=True)