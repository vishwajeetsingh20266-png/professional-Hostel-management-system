from datetime import date
from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from app import db
from app.models import Complaint, LeaveRequest, Notice, Attendance, Fee
student = Blueprint('student', __name__, url_prefix='/student')

@student.before_request
def check_student():
    if not current_user.is_authenticated or current_user.role != 'student': abort(403)

@student.route('/dashboard')
def dashboard():
    s=current_user.student
    notices=Notice.query.order_by(Notice.id.desc()).limit(5).all()
    pending_leaves=LeaveRequest.query.filter_by(student_id=s.id,status='Pending').count()
    open_complaints=Complaint.query.filter_by(student_id=s.id,status='Open').count()
    pending_fees=sum(f.amount for f in Fee.query.filter_by(student_id=s.id,status='Pending').all())
    attendance_count=Attendance.query.filter_by(student_id=s.id,status='Present').count()
    return render_template('student/dashboard.html', student=s, notices=notices, pending_leaves=pending_leaves, open_complaints=open_complaints, pending_fees=pending_fees, attendance_count=attendance_count)

@student.route('/leave', methods=['GET','POST'])
def leave():
    if request.method=='POST':
        f=request.form.get('from_date',''); t=request.form.get('to_date',''); reason=request.form.get('reason','').strip()
        if not f or not t or not reason: flash('All fields are required.', 'error')
        elif t < f: flash('To date cannot be before from date.', 'error')
        else: db.session.add(LeaveRequest(student_id=current_user.student.id,from_date=f,to_date=t,reason=reason)); db.session.commit(); flash('Leave request submitted.', 'success'); return redirect(url_for('student.leave'))
    return render_template('student/leave.html', leaves=LeaveRequest.query.filter_by(student_id=current_user.student.id).order_by(LeaveRequest.id.desc()).all())

@student.route('/complaint', methods=['GET','POST'])
def complaint():
    if request.method=='POST':
        subject=request.form.get('subject','').strip(); description=request.form.get('description','').strip()
        if subject and description: db.session.add(Complaint(student_id=current_user.student.id,subject=subject,description=description)); db.session.commit(); flash('Complaint submitted.', 'success'); return redirect(url_for('student.complaint'))
        flash('Subject and description are required.', 'error')
    return render_template('student/complaint.html', complaints=Complaint.query.filter_by(student_id=current_user.student.id).order_by(Complaint.id.desc()).all())

@student.route('/attendance', methods=['POST'])
def attendance():
    today=date.today().isoformat(); existing=Attendance.query.filter_by(student_id=current_user.student.id,date=today).first()
    if not existing: db.session.add(Attendance(student_id=current_user.student.id,date=today,status='Present')); db.session.commit(); flash('Today marked present.', 'success')
    else: flash('Attendance already marked for today.', 'error')
    return redirect(url_for('student.dashboard'))

@student.route('/fees')
def fees():
    return render_template('student/fees.html', fees=Fee.query.filter_by(student_id=current_user.student.id).order_by(Fee.id.desc()).all())
