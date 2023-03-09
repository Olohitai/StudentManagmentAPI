from flask import Flask
from flask_restx import Api
from flask_marshmallow import Marshmallow
from .students.views import student_namespace
from .auth.views import auth_namespace
from .courses.views import course_namespace
from .config.config import config_dict
from .utils import db, ma
from .models.student import Student
from .models.course import Course
from .models.grade import Grade
from .models.course_student import course_student
from flask_migrate import Migrate
from werkzeug.exceptions import NotFound, MethodNotAllowed

from flask_jwt_extended import JWTManager

# from flask_migrate import Migrate


def create_app(config=config_dict["dev"]):
    app = Flask(__name__)

    app.config.from_object(config)

    db.init_app(app)

    jwt = JWTManager(app)

    # create marshmallow object
    ma = Marshmallow(app)

    migrate = Migrate(app, db)

    @app.errorhandler(NotFound)
    def not_found(error):
        return {"error": "Not Found"}, 404

    @app.errorhandler(MethodNotAllowed)
    def method_not_allowed(error):
        return {"error": "Method Not Allowed"}, 405

    api = Api(app)
    api.add_namespace(course_namespace)
    api.add_namespace(auth_namespace, path="/auth")
    api.add_namespace(student_namespace, path="/students")

    @app.shell_context_processor
    def make_shell_context():
        return {
            "db": db,
            # 'User': User,
            "Course": Course,
            "Student": Student,
            "Grade": Grade,
        }

    return app
