from ..utils import db, ma
from datetime import datetime
 

class Course(db.Model): 
    __tablename__= 'courses'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    teacher = db.Column(db.String(50), nullable=False)
    students = db.relationship('Student', secondary='course_student', backref=db.backref('courses', lazy=True))
    grades = db.relationship('Grade', backref='course', lazy=True)

    def __repr__(self):
        return f'Course({self.name}, {self.teacher} )'



# Course Schema
class CourseSchema(ma.Schema):
    class Meta:
        model = Course
        fields = ("id", "name", "teacher", "students", "unit")

    students = ma.Nested('StudentSchema', many=True) 

 


# create Instance of Schema
course_schema = CourseSchema()
courses_schema = CourseSchema(many=True)
