from app import create_app
from app.extensions import db
from flask.cli import with_appcontext

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)