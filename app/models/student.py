from ..utils import db, ma


class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    
    def __repr__(self):
        return self.id




class StudentSchema(ma.Schema):
    class Meta:
        fields = ("name", "email")


# create Instance of Schema
student_schema = StudentSchema(many=False)
students_schema = StudentSchema(many=True)