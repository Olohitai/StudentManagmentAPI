
from ..utils import db, ma

from .course import Course
from .student import Student   

class Grade(db.Model):
    __tablenames__ = "grades"
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    grade = db.Column(db.Integer, nullable=False)
    
    def __repr__(self):
        return f'Grade({self.grade})'
    
class GradeSchema(ma.Schema):
    class Meta:
        fields = ("course_id", "student_id", "grade")

grade_schema = GradeSchema()
grades_schema = GradeSchema(many=True)  