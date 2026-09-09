from flask_login import UserMixin
from app import db, login_manager

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(30), nullable=False, default='student')
    student = db.relationship('Student', backref='user', uselist=False, cascade='all, delete-orphan')

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)
    roll_no = db.Column(db.String(50), unique=True, nullable=False)
    course = db.Column(db.String(120))
    phone = db.Column(db.String(30))
    guardian_name = db.Column(db.String(120))
    guardian_phone = db.Column(db.String(30))
    room_no = db.Column(db.String(30))
    status = db.Column(db.String(30), default='Active')

class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_no = db.Column(db.String(30), unique=True, nullable=False)
    floor = db.Column(db.String(30))
    capacity = db.Column(db.Integer, default=4)
    occupied = db.Column(db.Integer, default=0)
    status = db.Column(db.String(30), default='Available')

class LeaveRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    from_date = db.Column(db.String(20), nullable=False)
    to_date = db.Column(db.String(20), nullable=False)
    reason = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(30), default='Pending')
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    student = db.relationship('Student', backref='leave_requests')

class Complaint(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    subject = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(30), default='Open')
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    student = db.relationship('Student', backref='complaints')

class Notice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    content = db.Column(db.Text, nullable=False)
    priority = db.Column(db.String(30), default='Normal')
    created_at = db.Column(db.DateTime, server_default=db.func.now())

class Fee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    month = db.Column(db.String(30), nullable=False)
    status = db.Column(db.String(30), default='Pending')
    paid_at = db.Column(db.DateTime)
    student = db.relationship('Student', backref='fees')

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    date = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(30), default='Present')
    student = db.relationship('Student', backref='attendance')

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))
