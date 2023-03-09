# import unittest
# from .. import create_app
# from ..config.config import config_dict
# from ..models.student import Student
# from ..utils import db
# from flask_jwt_extended import create_access_token


# class StudentTestCase(unittest.TestCase):
#     def setUp(self):
#         self.app = create_app(config=config_dict["test"])
#         self.appctx = self.app.app_context()

#         self.appctx.push()

#         self.client = self.app.test_client()

#         db.create_all()

#     def tearDown(self):
#         db.drop_all()

#         self.app = None

#         self.appctx.pop()

#         self.client = None

#     def test_get_all_students(self):
#         token = create_access_token(identity="testuser")

#         headers = {"Authorization": f"Bearer {token}"}

#         response = self.client.get("/students/students", headers=headers)

#         assert response.status_code == 200

#         assert response.json == []


import unittest
from .. import create_app
from ..config.config import config_dict
from ..models.student import Student, student_schema
from ..utils import db
from flask_jwt_extended import create_access_token
import json
from flask.json import JSONEncoder
from ..models.student import Student


class StudentEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Student):
            return obj.to_dict()
        return super().default(obj)


class StudentTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(config=config_dict["test"])
        self.appctx = self.app.app_context()

        self.appctx.push()

        self.client = self.app.test_client()

        db.create_all()

        # Create a test student
        self.student = Student(name="Test Student", email="johndoe@gmail.com", id=1234)
        db.session.add(self.student)
        db.session.commit()
        return self.student

    def tearDown(self):
        db.session.remove()
        db.drop_all()

        self.app = None

        self.appctx.pop()

        self.client = None

    def test_get_all_students(self):
        token = create_access_token(identity="testuser")

        headers = {"Authorization": f"Bearer {token}"}

        response = self.client.get("/students/students", headers=headers)

        assert response.status_code == 200
        assert len(response.json) == 1

    def test_get_student(self):
        token = create_access_token(identity="testuser")

        headers = {"Authorization": f"Bearer {token}"}

        response = self.client.get(f"/students/{self.student.id}", headers=headers)

        assert response.status_code == 200

        assert response.json["name"] == self.student.name
        assert response.json["email"] == self.student.email

    def test_create_student(self):
        token = create_access_token(identity="testuser")

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        data = {"name": "New Student", "email": "John"}

        response = self.client.post("/students/students", json=data, headers=headers)
        response = student_schema.dump(response)
        assert response.status_code == 201
        assert response.get_data(as_text=True)["name"] == data["name"]

        token = create_access_token(identity="testuser")

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        data = {"name": "New Student", "email": "John"}

        response = self.client.post("/students/students", json=data, headers=headers)

        assert response.status_code == 201

        student = student_schema.load(response.json)

        # Dump the Student object back to JSON using the StudentSchema
        serialized_json = json.dumps(
            student, cls=StudentEncoder
        )  # use the custom encoder

        # Check the serialized JSON
        assert serialized_json == json.dumps(response.json, cls=StudentEncoder)

    def test_update_student(self):
        token = create_access_token(identity="testuser")

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        data = {"name": "Updated Student", "email": "Janedoe@gmail.com"}

        response = self.client.put(
            f"/students/{self.student.id}", json=data, headers=headers
        )

        assert response.status_code == 200
        assert response.json["name"] == data["name"]
        assert response.json["email"] == data["email"]

    def test_delete_student(self):
        token = create_access_token(identity="testuser")

        headers = {"Authorization": f"Bearer {token}"}

        response = self.client.delete(f"/students/{self.student.id}", headers=headers)

        assert response.status_code == 204
        assert Student.query.get(self.student.id) is None
