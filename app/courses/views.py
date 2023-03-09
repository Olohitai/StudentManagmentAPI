from flask_restx import Namespace, Resource
from flask import Flask, request, jsonify
from ..utils import db
from flask_restx import Namespace, Resource, fields, reqparse, abort
from ..models.course import Course
from ..models.student import Student
from ..models.users import User
from flask_jwt_extended import jwt_required, get_jwt_identity

# from ..models.users import User
from http import HTTPStatus
from ..models.course import Course, course_schema, courses_schema
from ..models.student import Student, student_schema, students_schema

course_namespace = Namespace("courses", description="A namespace for Courses")


@course_namespace.route("")
class createCourse(Resource):
    @course_namespace.doc(description="Retrieve all courses")
    def get(self):
        """
        Get all Courses

        """
        courses = Course.query.all()
        return courses_schema.dump(courses), 201

        # Return the serialized data as a JSON response
        # return jsonify(courses_data), 200

    @course_namespace.doc(description="Place an course")
    @jwt_required()
    def post(self):
        """

        Create a new course

        """
        username = get_jwt_identity()

        current_user = User.query.filter_by(username=username).first()
        name = request.json["name"]
        teacher = request.json["teacher"]

        course = Course(name=name, teacher=teacher)

        course.courses.append(current_user)

        db.session.add(course)
        db.session.commit()
        # course_schema.jsonify(course)

        return course_schema.dump(course), 201


@course_namespace.route("/course/<int:course_id>")
class GetUpdateDelete(Resource):
    @course_namespace.doc(
        description="Retrieve an course by ID",
        params={"course_id": "An ID for a given course"},
    )
    def get(self, course_id):
        """
        Retrieve an course by its id
        """

        course = Course.query.get_or_404(course_id)

        return course_schema.dump(course), 201

    @course_namespace.doc(
        description="Update an course given an course ID",
        params={"course_id": "An ID for a given course"},
    )
    @jwt_required()
    def put(self, course_id):
        """
        Update an Course with id
        """
        course = Course.query.get_or_404(course_id)
        name = request.json["name"]
        teacher = request.json["teacher"]

        course.name = name
        course.teacher = teacher

        db.session.commit()

        return course_schema.dump(course), 201

    @jwt_required()
    @course_namespace.doc(
        description="Delete an course given an course ID",
        params={"course_id": "An ID for a given course"},
    )
    def delete(self, course_id):
        """
        Delete an course with id
        """
        course = Course.query.get_or_404(course_id)

        db.session.delete(course)
        db.session.commit()

        return "", HTTPStatus.NO_CONTENT


@course_namespace.route("/<int:course_id>/enroll")
class EnrollStudent(Resource):
    @jwt_required()
    @course_namespace.doc(
        description="Enroll an student to course ",
        params={"course_id": "An ID for a given course"},
    )
    def post(self, course_id):
        """
        Enroll Student to Course
        """
        # course_id = request.json['course_id']
        course = Course.query.get_or_404(course_id)

        if not course:
            abort(HTTPStatus.NOT_FOUND, message="Course not found")

        data = request.json
        student_name = data.get("name")
        student_email = data.get("email")

        student = Student.query.filter_by(
            name=student_name, email=student_email
        ).first()
        if not student:
            abort(HTTPStatus.NOT_FOUND, message="Student not found")

        if student in course.students:
            abort(
                HTTPStatus.BAD_REQUEST,
                message="Student is already enrolled in this course",
            )
        course.students.append(student)

        db.session.commit()

        return course_schema.dump(course), 200


# Another Way to enroll student in a course using the student id and course
# @course_namespace.route("/<int:course_id>/students/<int:student_id>")
# class EnrollStudent(Resource):
#     @course_namespace.doc(
#         description="Enroll an student to course ",
#         params={"course_id": "An ID for a given course"},
#     )
#     def post(self, course_id, student_id):
#         """
#         Enroll Student to Course
#         """

#         student = Student.query.get_or_404(student_id)

#         # course_id = request.json['course_id']
#         course = Course.query.get_or_404(course_id)

#         course.students.append(student)

#         db.session.commit()

#         return course_schema.dump(course), 200


@course_namespace.route("/<int:course_id>/student")
class GetStudentsEnrolledInCourse(Resource):
    @course_namespace.doc(
        description="Enroll an student to course ",
        params={"course_id": "An ID for a given course"},
    )
    def get(self, course_id):
        """
        Get Students Enrolled in a course
        """

        # Get the course from the database
        course = Course.query.get_or_404(course_id)

        # Get the list of students registered for the course
        students = course.students

        # Serialize the student data
        result = students_schema.dump(students)

        # Return the serialized data
        return result, 200
