"""
SE-DBMS - Student Efficient Database Management System
Complete Flask Web Application with SQLite Database

Project Structure:
sedbms/
├── app.py (this file)
├── sedbms.db (auto-created)
├── templates/
│   ├── base.html
│   ├── login.html
│   ├── dashboard.html
│   ├── students.html
│   ├── subjects.html
│   ├── marks.html
│   └── reports.html
└── static/
    └── style.css

Installation:
pip install flask

Run:
python app.py

Access at: http://localhost:5000
"""

from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import hashlib
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production'

DB_NAME = 'sedbms.db'

# ==================== DATABASE FUNCTIONS ====================

def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database with tables and sample data"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('admin', 'faculty', 'student')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Students table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            usn TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            branch TEXT NOT NULL,
            admission_year INTEGER NOT NULL,
            current_semester INTEGER NOT NULL CHECK(current_semester BETWEEN 1 AND 8),
            email TEXT,
            phone TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Subjects table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS subjects (
            code TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            credits INTEGER NOT NULL CHECK(credits BETWEEN 1 AND 6),
            semester INTEGER NOT NULL CHECK(semester BETWEEN 1 AND 8),
            subject_type TEXT DEFAULT 'Theory'
        )
    ''')
    
    # Marks table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS marks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usn TEXT NOT NULL,
            subject_code TEXT NOT NULL,
            semester INTEGER NOT NULL CHECK(semester BETWEEN 1 AND 8),
            cie_marks INTEGER NOT NULL CHECK(cie_marks BETWEEN 0 AND 50),
            see_marks INTEGER NOT NULL CHECK(see_marks BETWEEN 0 AND 100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (usn) REFERENCES students(usn) ON DELETE CASCADE,
            FOREIGN KEY (subject_code) REFERENCES subjects(code) ON DELETE CASCADE,
            UNIQUE(usn, subject_code, semester)
        )
    ''')
    
    # Insert default users
    default_users = [
        ('admin', 'admin123', 'admin'),
        ('faculty', 'faculty123', 'faculty'),
        ('student', 'student123', 'student')
    ]
    
    for username, password, role in default_users:
        hashed_pwd = hashlib.sha256(password.encode()).hexdigest()
        try:
            cursor.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)',
                         (username, hashed_pwd, role))
        except sqlite3.IntegrityError:
            pass
    
    # Insert sample data
    sample_students = [
        ('1CR21CS001', 'Rahul Kumar', 'CSE', 2021, 6, 'rahul@example.com', '9876543210'),
        ('1CR21CS002', 'Priya Sharma', 'CSE', 2021, 6, 'priya@example.com', '9876543211'),
        ('1CR21EC001', 'Amit Patel', 'ECE', 2021, 6, 'amit@example.com', '9876543212'),
        ('1CR22CS001', 'Sneha Reddy', 'CSE', 2022, 4, 'sneha@example.com', '9876543213'),
    ]
    
    for student in sample_students:
        try:
            cursor.execute('''INSERT INTO students 
                           (usn, name, branch, admission_year, current_semester, email, phone) 
                           VALUES (?, ?, ?, ?, ?, ?, ?)''', student)
        except sqlite3.IntegrityError:
            pass
    
    sample_subjects = [
        ('CS601', 'Database Management Systems', 4, 6, 'Theory'),
        ('CS602', 'Computer Networks', 4, 6, 'Theory'),
        ('CS603', 'Software Engineering', 3, 6, 'Theory'),
        ('CS401', 'Data Structures', 4, 4, 'Theory'),
        ('CS402', 'Operating Systems', 4, 4, 'Theory'),
    ]
    
    for subject in sample_subjects:
        try:
            cursor.execute('''INSERT INTO subjects 
                           (code, name, credits, semester, subject_type) 
                           VALUES (?, ?, ?, ?, ?)''', subject)
        except sqlite3.IntegrityError:
            pass
    
    sample_marks = [
        ('1CR21CS001', 'CS601', 6, 45, 85),
        ('1CR21CS001', 'CS602', 6, 42, 80),
        ('1CR21CS001', 'CS603', 6, 48, 88),
    ]
    
    for mark in sample_marks:
        try:
            cursor.execute('''INSERT INTO marks 
                           (usn, subject_code, semester, cie_marks, see_marks) 
                           VALUES (?, ?, ?, ?, ?)''', mark)
        except sqlite3.IntegrityError:
            pass
    
    conn.commit()
    conn.close()
    print("✓ Database initialized successfully!")

# ==================== HELPER FUNCTIONS ====================

def calculate_grade_point(total_marks):
    """Calculate grade point based on total marks"""
    if total_marks >= 135: return 10
    if total_marks >= 120: return 9
    if total_marks >= 105: return 8
    if total_marks >= 90: return 7
    if total_marks >= 75: return 6
    if total_marks >= 60: return 5
    return 0

def calculate_sgpa(usn, semester):
    """Calculate SGPA for a student in a semester"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT m.cie_marks, m.see_marks, s.credits
        FROM marks m
        JOIN subjects s ON m.subject_code = s.code
        WHERE m.usn = ? AND m.semester = ?
    ''', (usn, semester))
    
    results = cursor.fetchall()
    conn.close()
    
    if not results:
        return 0.0
    
    total_grade_points = 0
    total_credits = 0
    
    for row in results:
        total_marks = row['cie_marks'] + row['see_marks']
        grade_point = calculate_grade_point(total_marks)
        total_grade_points += grade_point * row['credits']
        total_credits += row['credits']
    
    return round(total_grade_points / total_credits, 2) if total_credits > 0 else 0.0

def calculate_cgpa(usn):
    """Calculate CGPA for a student across all completed semesters"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Get all marks for the student grouped by semester
    cursor.execute('''
        SELECT m.semester, m.cie_marks, m.see_marks, s.credits
        FROM marks m
        JOIN subjects s ON m.subject_code = s.code
        WHERE m.usn = ?
        ORDER BY m.semester
    ''', (usn,))
    
    all_marks = cursor.fetchall()
    conn.close()
    
    if not all_marks:
        return 0.0
    
    # Calculate overall CGPA using all subjects across all semesters
    total_grade_points = 0
    total_credits = 0
    
    for row in all_marks:
        total_marks = row['cie_marks'] + row['see_marks']
        grade_point = calculate_grade_point(total_marks)
        
        # Only count if grade is passing (> 0)
        if grade_point > 0:
            credit_points = grade_point * row['credits']
            total_grade_points += credit_points
            total_credits += row['credits']
    
    if total_credits == 0:
        return 0.0
    
    cgpa = total_grade_points / total_credits
    return round(cgpa, 2)

# ==================== ROUTES ====================

@app.route('/')
def index():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        hashed_pwd = hashlib.sha256(password.encode()).hexdigest()
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT username, role FROM users WHERE username = ? AND password = ?',
                      (username, hashed_pwd))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            session['user'] = {'username': user['username'], 'role': user['role']}
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials!', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('Logged out successfully!', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Get statistics
    cursor.execute('SELECT COUNT(*) as count FROM students')
    total_students = cursor.fetchone()['count']
    
    cursor.execute('SELECT COUNT(*) as count FROM subjects')
    total_subjects = cursor.fetchone()['count']
    
    cursor.execute('SELECT usn FROM students')
    students = cursor.fetchall()
    
    total_cgpa = sum(calculate_cgpa(s['usn']) for s in students)
    avg_cgpa = round(total_cgpa / total_students, 2) if total_students > 0 else 0.0
    
    # Get recent students
    cursor.execute('SELECT * FROM students ORDER BY created_at DESC LIMIT 5')
    recent_students = cursor.fetchall()
    
    conn.close()
    
    students_with_cgpa = []
    for student in recent_students:
        s_dict = dict(student)
        s_dict['cgpa'] = calculate_cgpa(student['usn'])
        students_with_cgpa.append(s_dict)
    
    return render_template('dashboard.html', 
                         total_students=total_students,
                         total_subjects=total_subjects,
                         avg_cgpa=avg_cgpa,
                         recent_students=students_with_cgpa)

@app.route('/students', methods=['GET', 'POST'])
def students():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        try:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO students (usn, name, branch, admission_year, current_semester, email, phone)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                request.form.get('usn').upper(),
                request.form.get('name'),
                request.form.get('branch'),
                request.form.get('year'),
                request.form.get('semester'),
                request.form.get('email'),
                request.form.get('phone')
            ))
            conn.commit()
            conn.close()
            flash('Student added successfully!', 'success')
        except sqlite3.IntegrityError:
            flash('Student with this USN already exists!', 'danger')
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')
        
        return redirect(url_for('students'))
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM students ORDER BY usn')
    all_students = cursor.fetchall()
    conn.close()
    
    students_with_cgpa = []
    for student in all_students:
        s_dict = dict(student)
        s_dict['cgpa'] = calculate_cgpa(student['usn'])
        students_with_cgpa.append(s_dict)
    
    return render_template('students.html', students=students_with_cgpa)

@app.route('/subjects', methods=['GET', 'POST'])
def subjects():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        try:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO subjects (code, name, credits, semester, subject_type)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                request.form.get('code').upper(),
                request.form.get('name'),
                request.form.get('credits'),
                request.form.get('semester'),
                request.form.get('type', 'Theory')
            ))
            conn.commit()
            conn.close()
            flash('Subject added successfully!', 'success')
        except sqlite3.IntegrityError:
            flash('Subject with this code already exists!', 'danger')
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')
        
        return redirect(url_for('subjects'))
    
    semester = request.args.get('semester', '')
    
    conn = get_db()
    cursor = conn.cursor()
    
    if semester:
        cursor.execute('SELECT * FROM subjects WHERE semester = ? ORDER BY code', (semester,))
    else:
        cursor.execute('SELECT * FROM subjects ORDER BY semester, code')
    
    all_subjects = cursor.fetchall()
    conn.close()
    
    return render_template('subjects.html', subjects=all_subjects, selected_semester=semester)

@app.route('/marks', methods=['GET', 'POST'])
def marks():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        try:
            conn = get_db()
            cursor = conn.cursor()
            
            usn = request.form.get('usn')
            subject_code = request.form.get('subject_code')
            semester = request.form.get('semester')
            
            # Check if marks exist
            cursor.execute('''
                SELECT id FROM marks 
                WHERE usn = ? AND subject_code = ? AND semester = ?
            ''', (usn, subject_code, semester))
            
            existing = cursor.fetchone()
            
            if existing:
                cursor.execute('''
                    UPDATE marks 
                    SET cie_marks = ?, see_marks = ?
                    WHERE id = ?
                ''', (request.form.get('cie'), request.form.get('see'), existing['id']))
                flash('Marks updated successfully!', 'success')
            else:
                cursor.execute('''
                    INSERT INTO marks (usn, subject_code, semester, cie_marks, see_marks)
                    VALUES (?, ?, ?, ?, ?)
                ''', (usn, subject_code, semester, 
                     request.form.get('cie'), request.form.get('see')))
                flash('Marks added successfully!', 'success')
            
            conn.commit()
            conn.close()
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')
        
        return redirect(url_for('marks'))
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT m.*, s.name as student_name, sub.name as subject_name, sub.credits
        FROM marks m
        JOIN students s ON m.usn = s.usn
        JOIN subjects sub ON m.subject_code = sub.code
        ORDER BY m.usn, m.semester
    ''')
    
    all_marks = []
    for row in cursor.fetchall():
        mark = dict(row)
        total = mark['cie_marks'] + mark['see_marks']
        mark['total'] = total
        mark['grade'] = calculate_grade_point(total)
        all_marks.append(mark)
    
    cursor.execute('SELECT usn, name FROM students ORDER BY usn')
    all_students = cursor.fetchall()
    
    cursor.execute('SELECT code, name FROM subjects ORDER BY code')
    all_subjects = cursor.fetchall()
    
    conn.close()
    
    return render_template('marks.html', marks=all_marks, 
                         students=all_students, subjects=all_subjects)

@app.route('/reports')
def reports():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    usn = request.args.get('usn', '')
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT usn, name FROM students ORDER BY usn')
    all_students = cursor.fetchall()
    
    student_data = None
    marks_data = []
    cgpa = 0.0
    semester_data = {}  # To store marks grouped by semester
    semester_sgpa = {}  # To store SGPA for each semester
    
    if usn:
        cursor.execute('SELECT * FROM students WHERE usn = ?', (usn,))
        student_data = cursor.fetchone()
        
        if student_data:
            cursor.execute('''
                SELECT m.*, s.name as subject_name, s.credits, s.semester
                FROM marks m
                JOIN subjects s ON m.subject_code = s.code
                WHERE m.usn = ?
                ORDER BY m.semester, m.subject_code
            ''', (usn,))
            
            for row in cursor.fetchall():
                mark = dict(row)
                total = mark['cie_marks'] + mark['see_marks']
                mark['total'] = total
                mark['grade'] = calculate_grade_point(total)
                marks_data.append(mark)
                
                # Group marks by semester
                sem = mark['semester']
                if sem not in semester_data:
                    semester_data[sem] = []
                semester_data[sem].append(mark)
            
            # Calculate SGPA for each semester
            for sem in semester_data:
                semester_sgpa[sem] = calculate_sgpa(usn, sem)
            
            cgpa = calculate_cgpa(usn)
    
    conn.close()
    
    return render_template('reports.html', 
                         students=all_students,
                         selected_usn=usn,
                         student=student_data,
                         marks=marks_data,
                         cgpa=cgpa,
                         semester_data=semester_data,
                         semester_sgpa=semester_sgpa)
@app.route('/students/delete/<usn>', methods=['POST'])
def delete_student(usn):
    if 'user' not in session:
        return redirect(url_for('login'))
    
    # Only Admin can delete students
    if session['user']['role'] != 'admin':
        flash('Access denied! Only administrators can delete students.', 'danger')
        return redirect(url_for('students'))
    
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # Check if student exists
        cursor.execute('SELECT name FROM students WHERE usn = ?', (usn,))
        student = cursor.fetchone()
        
        if student:
            # Delete student (will cascade delete marks due to foreign key)
            cursor.execute('DELETE FROM students WHERE usn = ?', (usn,))
            conn.commit()
            flash(f'Student {usn} - {student["name"]} deleted successfully!', 'success')
        else:
            flash('Student not found!', 'warning')
        
        conn.close()
    except Exception as e:
        flash(f'Error deleting student: {str(e)}', 'danger')
    
    return redirect(url_for('students'))
# ==================== MAIN ====================

if __name__ == '__main__':
    # Create templates and static directories
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    # Initialize database
    init_db()
    
    
    print("\n" + "="*60)
    print("SE-DBMS - Student Effiecient : Database Management System")
    print("="*60)
    print(f"\n✓ Database: {DB_NAME}")
    print("\n📝 Default Login Credentials:")
    print("   Admin:   username='admin'   password='admin123'")
    print("   Faculty: username='faculty' password='faculty123'")
    print("   Student: username='student' password='student123'")
    print("\n🌐 Server starting at: http://localhost:5000")
    print("\n⚠️  Make sure HTML templates are in 'templates/' folder!")
    print("="*60 + "\n")
    
    app.run(debug=True, port=5000)