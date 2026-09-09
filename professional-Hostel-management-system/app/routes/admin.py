from datetime import datetime
from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from werkzeug.security import generate_password_hash
from app import db
from app.models import Complaint, LeaveRequest, Notice, Room, Student, User, Fee

admin = Blueprint('admin', __name__, url_prefix='/admin')

@admin.before_request
def check_admin():
    if not current_user.is_authenticated or current_user.role != 'admin':
        abort(403)

@admin.route('/dashboard')
def dashboard():
    students = Student.query.count()
    rooms = Room.query.count()
    pending_leaves = LeaveRequest.query.filter_by(status='Pending').count()
    open_complaints = Complaint.query.filter_by(status='Open').count()
    occupied = sum(r.occupied for r in Room.query.all())
    capacity = sum(r.capacity for r in Room.query.all())
    pending_fees = sum((f.amount for f in Fee.query.filter_by(status='Pending').all()), 0)
    notices = Notice.query.order_by(Notice.id.desc()).limit(4).all()
    recent_leaves = LeaveRequest.query.order_by(LeaveRequest.id.desc()).limit(5).all()
    return render_template('admin/dashboard.html', students=students, rooms=rooms, leaves=pending_leaves, complaints=open_complaints, occupied=occupied, capacity=capacity, pending_fees=pending_fees, notices=notices, recent_leaves=recent_leaves)

@admin.route('/students')
def students():
    q = request.args.get('q', '').strip()
    query = Student.query.join(User)
    if q:
        like = f'%{q}%'
        query = query.filter((User.name.ilike(like)) | (Student.roll_no.ilike(like)) | (Student.course.ilike(like)))
    return render_template('admin/students.html', students=query.order_by(Student.id.desc()).all(), q=q)

@admin.route('/students/add', methods=['GET','POST'])
def add_student():
    if request.method == 'POST':
        data = {k: request.form.get(k, '').strip() for k in ['name','email','password','roll_no','course','phone','guardian_name','guardian_phone','room_no']}
        if not all([data['name'], data['email'], data['password'], data['roll_no']]):
            flash('Name, email, password and roll number are required.', 'error'); return render_template('admin/add_student.html')
        if User.query.filter_by(email=data['email']).first(): flash('Email already exists.', 'error'); return render_template('admin/add_student.html')
        if Student.query.filter_by(roll_no=data['roll_no']).first(): flash('Roll number already exists.', 'error'); return render_template('admin/add_student.html')
        user = User(name=data['name'], email=data['email'], password=generate_password_hash(data['password']), role='student')
        db.session.add(user); db.session.flush()
        student = Student(user_id=user.id, roll_no=data['roll_no'], course=data['course'], phone=data['phone'], guardian_name=data['guardian_name'], guardian_phone=data['guardian_phone'], room_no=data['room_no'] or None)
        db.session.add(student)
        if data['room_no']:
            room = Room.query.filter_by(room_no=data['room_no']).first()
            if room and room.occupied < room.capacity: room.occupied += 1; room.status = 'Full' if room.occupied >= room.capacity else 'Available'
        db.session.commit(); flash('Student added successfully.', 'success'); return redirect(url_for('admin.students'))
    return render_template('admin/add_student.html')

@admin.route('/rooms', methods=['GET','POST'])
def rooms():
    if request.method == 'POST':
        room_no = request.form.get('room_no','').strip()
        try: capacity = max(1, int(request.form.get('capacity', 4)))
        except ValueError: capacity = 4
        if Room.query.filter_by(room_no=room_no).first(): flash('Room already exists.', 'error')
        elif not room_no: flash('Room number is required.', 'error')
        else:
            db.session.add(Room(room_no=room_no, floor=request.form.get('floor','').strip(), capacity=capacity, occupied=0, status='Available')); db.session.commit(); flash('Room added successfully.', 'success')
    return render_template('admin/rooms.html', rooms=Room.query.order_by(Room.room_no).all())

@admin.route('/rooms/<int:room_id>/delete', methods=['POST'])
def delete_room(room_id):
    room = Room.query.get_or_404(room_id)
    if room.occupied: flash('Cannot delete an occupied room.', 'error')
    else: db.session.delete(room); db.session.commit(); flash('Room deleted.', 'success')
    return redirect(url_for('admin.rooms'))

@admin.route('/leaves')
def leaves():
    return render_template('admin/leaves.html', leaves=LeaveRequest.query.order_by(LeaveRequest.id.desc()).all())

@admin.route('/leaves/<int:leave_id>/<status>', methods=['POST'])
def update_leave(leave_id, status):
    if status not in {'Approved','Rejected','Pending'}: abort(400)
    leave = LeaveRequest.query.get_or_404(leave_id); leave.status = status; db.session.commit(); flash(f'Leave {status.lower()}.', 'success'); return redirect(url_for('admin.leaves'))

@admin.route('/complaints')
def complaints():
    return render_template('admin/complaints.html', complaints=Complaint.query.order_by(Complaint.id.desc()).all())

@admin.route('/complaints/<int:complaint_id>/<status>', methods=['POST'])
def update_complaint(complaint_id, status):
    if status not in {'Resolved','Open'}: abort(400)
    complaint = Complaint.query.get_or_404(complaint_id); complaint.status = status; db.session.commit(); flash('Complaint updated.', 'success'); return redirect(url_for('admin.complaints'))

@admin.route('/notices', methods=['GET','POST'])
def notices():
    if request.method == 'POST':
        title=request.form.get('title','').strip(); content=request.form.get('content','').strip(); priority=request.form.get('priority','Normal')
        if title and content: db.session.add(Notice(title=title, content=content, priority=priority)); db.session.commit(); flash('Notice published successfully.', 'success')
        else: flash('Title and content are required.', 'error')
    return render_template('admin/notices.html', notices=Notice.query.order_by(Notice.id.desc()).all())

@admin.route('/fees', methods=['GET','POST'])
def fees():
    if request.method == 'POST':
        try: amount=float(request.form.get('amount','0'))
        except ValueError: amount=0
        student_id=request.form.get('student_id'); month=request.form.get('month','').strip()
        if amount <= 0 or not student_id or not month: flash('Student, month and valid amount are required.', 'error')
        else: db.session.add(Fee(student_id=int(student_id), amount=amount, month=month)); db.session.commit(); flash('Fee record added.', 'success')
    return render_template('admin/fees.html', fees=Fee.query.order_by(Fee.id.desc()).all(), students=Student.query.order_by(Student.roll_no).all())

@admin.route('/fees/<int:fee_id>/paid', methods=['POST'])
def mark_fee_paid(fee_id):
    fee=Fee.query.get_or_404(fee_id); fee.status='Paid'; fee.paid_at=datetime.utcnow(); db.session.commit(); flash('Fee marked as paid.', 'success'); return redirect(url_for('admin.fees'))
