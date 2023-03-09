from flask_restx import Namespace, Resource
from flask import Flask, request, jsonify
from ..utils import db
from flask_restx import Namespace, Resource, fields, reqparse, abort
from ..models.course import Course
from ..models.grade import Grade, grade_schema, grades_schema
from flask_jwt_extended import jwt_required, get_jwt_identity

# from ..models.users import User
from http import HTTPStatus
from ..models.student import Student, student_schema, students_schema

student_namespace = Namespace("students", description="A namespace for Students")


@student_namespace.route("/students")
class createStudent(Resource):
    @student_namespace.doc(description="Retrieve all students")
    def get(self):
        """
        Get all Students

        """
        students = Student.query.all()
        return students_schema.dump(students), 200

        # Return the serialized data as a JSON response
        # return jsonify(students_data), 200

    @jwt_required
    @student_namespace.doc(description="Place an student")
    def post(self):
        """

        Create a new student

        """

        name = request.json["name"]
        email = request.json["email"]

        student = Student(name=name, email=email)

        db.session.add(student)
        db.session.commit()
        # student_schema.jsonify(student)

        return student_schema.dump(student), 201


@student_namespace.route("/<int:student_id>")
class GetUpdateDelete(Resource):
    @student_namespace.doc(
        description="Retrieve a student by ID",
        params={"student_id": "An ID for a given student"},
    )
    def get(self, student_id):
        """
        Retrieve an student by its id
        """

        student = Student.query.get_or_404(student_id)

        return student_schema.dump(student), 200

    @student_namespace.doc(
        description="Update an student given an student ID",
        params={"student_id": "An ID for a given student"},
    )
    @jwt_required()
    def put(self, student_id):
        """
        Update an Student with id
        """
        student = Student.query.get_or_404(student_id)
        name = request.json["name"]
        email = request.json["email"]

        student.name = name
        student.email = email

        db.session.commit()

        return student_schema.dump(student), 200

    @jwt_required()
    @student_namespace.doc(
        description="Delete an student given an student ID",
        params={"student_id": "An ID for a given student"},
    )
    def delete(self, student_id):
        """
        Delete an student with id
        """
        student = Student.query.get_or_404(student_id)

        db.session.delete(student)
        db.session.commit()

        return "", HTTPStatus.NO_CONTENT


@student_namespace.route("/<int:course_id>/student")
class GetStudentsEnrolledInCourse(Resource):
    @student_namespace.doc(
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


@student_namespace.route("/<int:course_id>/students/<int:student_id>/grades")
class CreateGetGradeForStudentInCourse(Resource):
    @jwt_required
    @student_namespace.doc(
        description="Get grade for a student ",
        params={"course_id": "An ID for a given course"},
    )
    def get(self, student_id, course_id):
        """
        Retrieve grades for student in a course
        """

        # Get the grade for the student in the course from the database
        grade = Grade.query.filter_by(
            course_id=course_id, student_id=student_id
        ).first()

        if not grade:
            return ({"error": "Grade not found"}), 404

        # Get the corresponding course and student objects
        course = Course.query.get_or_404(course_id)
        student = Student.query.get_or_404(student_id)

        # Serialize the grade data
        result = grade_schema.dump(grade)

        # Include the course name and student name in the response
        result["course_name"] = course.name
        result["student_name"] = student.name

        # Return the serialized data
        return result, 200

    @student_namespace.doc(
        description="Create grade for a course ",
        params={"course_id": "An ID for a given course"},
    )
    def post(self, course_id, student_id):
        """
        Create Grade for a course
        """

        course = Course.query.get_or_404(course_id)
        student = Student.query.get_or_404(student_id)

        grade_value = request.json["grade"]
        grade = Grade(course_id=course.id, student_id=student.id, grade=grade_value)

        # Check if the course and student are associated
        if student not in course.students:
            abort(HTTPStatus.NOT_FOUND, message="Student is not Registerd to Course")

        # if grade in course.students:
        #     abort(HTTPStatus.BAD_REQUEST, message="Student is already enrolled in this course")

        db.session.add(grade)
        db.session.commit()

        return grade_schema.dump(grade), 201

    #     return ({
    #     'id': grade.id,
    #     'course_id': grade.course_id,
    #     'student_id': grade.student_id.name,
    #     'grade': grade.grade
    # }), 201


@student_namespace.route("/<int:student_id>/grades")
class AllGradeForStudent(Resource):
    @student_namespace.doc(
        description="Get all grade for a student ",
        params={"course_id": "An ID for a given course"},
    )
    def get(self, student_id):
        """
        Get all Grade for a Student
        """

        # Get all the grades for the student from the database
        grades = Grade.query.filter_by(student_id=student_id).all()

        # Serialize the grade data
        result = grades_schema.dump(grades)

        # Return the serialized data
        return result, 200


@student_namespace.route("/<int:student_id>/gpa")
class GpaForStudent(Resource):
    @student_namespace.doc(
        description="Get all grade for a student ",
        params={"course_id": "An ID for a given course"},
    )
    def get(self, student_id):
        """
        Get student gpa for a Student
        """
        student = Student.query.get_or_404(student_id)
        # Get all grades for the student from the database
        grades = Grade.query.filter_by(student_id=student_id).all()

        # Calculate total grade points and credits

        total_grade_points = 0
        total_credits = 0
        for grade in grades:
            score = grade.grade
        if score >= 70:
            grade_points = 5
        elif score >= 60:
            grade_points = 4
        elif score >= 50:
            grade_points = 3
        elif score >= 45:
            grade_points = 2
        elif score >= 40:
            grade_points = 1
        else:
            grade_points = 0

        total_grade_points += grade_points
        total_credits += 1

        # Calculate GPA
        gpa = total_grade_points / total_credits

        # Return the calculated GPA
        return ({"gpa": gpa, "student_name": student.name}), 200
