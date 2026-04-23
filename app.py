from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'super_secret_dental_key'  # In production, use a secure random key

DB_FILE = 'database.db'

# Admin Credentials
ADMIN_USER = 'admin'
ADMIN_PASS = 'password123'

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    # Create appointments table
    c.execute('''
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER,
            phone TEXT NOT NULL,
            email TEXT,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            problem TEXT,
            status TEXT DEFAULT 'Pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    # Create feedbacks table
    c.execute('''
        CREATE TABLE IF NOT EXISTS feedbacks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_name TEXT,
            rating INTEGER,
            comments TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    conn = get_db_connection()
    # Fetch some recent feedbacks to display
    feedbacks = conn.execute('SELECT * FROM feedbacks ORDER BY created_at DESC LIMIT 5').fetchall()
    conn.close()
    return render_template('index.html', feedbacks=feedbacks)

@app.route('/book', methods=['POST'])
def book():
    try:
        name = request.form.get('name')
        age = request.form.get('age')
        phone = request.form.get('phone')
        email = request.form.get('email')
        date = request.form.get('date')
        time = request.form.get('time')
        problem = request.form.get('problem')
        
        if not all([name, phone, date, time]):
            return jsonify({'success': False, 'message': 'Please fill all required fields.'}), 400

        conn = get_db_connection()
        conn.execute('''
            INSERT INTO appointments (name, age, phone, email, date, time, problem)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (name, age, phone, email, date, time, problem))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Appointment booked successfully!'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/feedback', methods=['POST'])
def feedback():
    try:
        name = request.form.get('patient_name', 'Anonymous')
        rating = request.form.get('rating')
        comments = request.form.get('comments')
        
        if not rating:
            return jsonify({'success': False, 'message': 'Rating is required.'}), 400

        conn = get_db_connection()
        conn.execute('''
            INSERT INTO feedbacks (patient_name, rating, comments)
            VALUES (?, ?, ?)
        ''', (name, rating, comments))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Feedback submitted. Thank you!'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if 'admin_logged_in' in session:
        return redirect('/dashboard')
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == ADMIN_USER and password == ADMIN_PASS:
            session['admin_logged_in'] = True
            return redirect('/dashboard')
        else:
            flash('Invalid credentials. Please try again.', 'error')
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    return redirect('/admin')

@app.route('/dashboard')
def dashboard():
    if 'admin_logged_in' not in session:
        return redirect('/admin')
        
    search = request.args.get('search', '')
    status_filter = request.args.get('status', '')
    
    conn = get_db_connection()
    query = 'SELECT * FROM appointments WHERE 1=1'
    params = []
    
    if search:
        query += ' AND (name LIKE ? OR phone LIKE ?)'
        params.extend([f'%{search}%', f'%{search}%'])
        
    if status_filter:
        query += ' AND status = ?'
        params.append(status_filter)
        
    query += ' ORDER BY date DESC, time DESC'
    
    appointments = conn.execute(query, params).fetchall()
    conn.close()
    
    return render_template('dashboard.html', appointments=appointments, search=search, status=status_filter)

@app.route('/dashboard/delete/<int:id>', methods=['POST'])
def delete_appointment(id):
    if 'admin_logged_in' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
        
    conn = get_db_connection()
    conn.execute('DELETE FROM appointments WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    
    return redirect('/dashboard')

@app.route('/dashboard/complete/<int:id>', methods=['POST'])
def complete_appointment(id):
    if 'admin_logged_in' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
        
    conn = get_db_connection()
    conn.execute('UPDATE appointments SET status = ? WHERE id = ?', ('Completed', id))
    conn.commit()
    conn.close()
    
    return redirect('/dashboard')

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
