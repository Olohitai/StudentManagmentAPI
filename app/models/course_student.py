from ..utils import db

course_student = db.Table('course_student',
    db.Column('course_id', db.Integer, db.ForeignKey('courses.id')),
    db.Column('student_id', db.Integer, db.ForeignKey('students.id'))
) 

