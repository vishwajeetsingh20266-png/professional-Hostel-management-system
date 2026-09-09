import os
from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please login to continue.'

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    os.makedirs(app.instance_path, exist_ok=True)
    app.config.update(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'hostel-dashboard-secret-change-me'),
        SQLALCHEMY_DATABASE_URI='sqlite:///' + os.path.join(app.instance_path, 'hostel.db'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )
    db.init_app(app)
    login_manager.init_app(app)

    from app.routes.auth import auth
    from app.routes.admin import admin
    from app.routes.student import student
    app.register_blueprint(auth)
    app.register_blueprint(admin)
    app.register_blueprint(student)

    with app.app_context():
        from app.models import User, Student, Room, Notice, Fee
        db.create_all()
        seed_demo_data()
    return app

def seed_demo_data():
    from app.models import User, Student, Room, Notice, Fee
    admin = User.query.filter_by(email='admin@hostel.com').first()
    if not admin:
        db.session.add(User(name='Hostel Admin', email='admin@hostel.com', password=generate_password_hash('admin123'), role='admin'))
    student_user = User.query.filter_by(email='student@hostel.com').first()
    if not student_user:
        student_user = User(name='Demo Student', email='student@hostel.com', password=generate_password_hash('student123'), role='student')
        db.session.add(student_user)
        db.session.flush()
        db.session.add(Student(user_id=student_user.id, roll_no='GH001', course='B.Sc Computer Science', phone='9876543210', guardian_name='Parent', guardian_phone='9876543211', room_no='A-101'))
    if Room.query.count() == 0:
        db.session.add_all([
            Room(room_no='A-101', floor='1st Floor', capacity=4, occupied=1, status='Available'),
            Room(room_no='A-102', floor='1st Floor', capacity=4, occupied=3, status='Available'),
            Room(room_no='B-201', floor='2nd Floor', capacity=3, occupied=3, status='Full'),
            Room(room_no='B-202', floor='2nd Floor', capacity=3, occupied=0, status='Available'),
            Room(room_no='C-301', floor='3rd Floor', capacity=4, occupied=2, status='Available'),
        ])
    if Notice.query.count() == 0:
        db.session.add_all([
            Notice(title='Monthly Hostel Meeting', content='All residents should attend the monthly hostel meeting at 6:00 PM.', priority='High'),
            Notice(title='Mess Timing Update', content='Dinner will be served from 7:30 PM to 9:30 PM from Monday.', priority='Normal'),
        ])
    db.session.commit()
