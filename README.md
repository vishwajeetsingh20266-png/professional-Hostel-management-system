# HostelHub – Girls Hostel Management System

A complete Flask + SQLite hostel management application with a modern responsive dashboard.

## Features
- Admin and Student login
- Resident management
- Room and bed management
- Leave request workflow
- Complaint workflow
- Hostel notices
- Fee records and payment status
- Student attendance
- Responsive sidebar dashboard

## Demo credentials
Admin: `admin@hostel.com` / `admin123`
Student: `student@hostel.com` / `student123`

## Run on Windows
```powershell
python -m venv venv
.\venv\Scripts\python.exe -m pip install -r requirements.txt
.\venv\Scripts\python.exe run.py
```
Open http://127.0.0.1:5000

The SQLite database is created automatically in `instance/hostel.db`.
