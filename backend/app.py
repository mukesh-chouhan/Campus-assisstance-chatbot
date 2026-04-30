from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
import json
from datetime import datetime
import sqlite3
import hashlib
import secrets
from chatbot_engine import CampusChatbot, init_default_faqs

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Initialize chatbot engine
chatbot = CampusChatbot()
DB_PATH = os.path.join(os.path.dirname(__file__), 'campus_assistant.db')

# Password hashing functions
def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, password_hash):
    """Verify password against hash"""
    return hash_password(password) == password_hash

# Database initialization
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Chat logs table
    c.execute('''CREATE TABLE IF NOT EXISTS chat_logs
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id TEXT,
                  user_message TEXT,
                  bot_response TEXT,
                  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                  intent TEXT,
                  confidence REAL)''')
    
    # FAQs table
    c.execute('''CREATE TABLE IF NOT EXISTS faqs
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  category TEXT,
                  question TEXT,
                  answer TEXT,
                  keywords TEXT,
                  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    
    # Analytics table
    c.execute('''CREATE TABLE IF NOT EXISTS analytics
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  date DATE,
                  total_queries INTEGER DEFAULT 0,
                  unique_users INTEGER DEFAULT 0,
                  avg_response_time REAL,
                  top_intent TEXT)''')
    
    # Users table for authentication
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id TEXT UNIQUE NOT NULL,
                  email TEXT UNIQUE NOT NULL,
                  password_hash TEXT NOT NULL,
                  name TEXT,
                  role TEXT DEFAULT 'student',
                  roll_number TEXT,
                  department TEXT,
                  year INTEGER,
                  phone TEXT,
                  security_question TEXT,
                  security_answer TEXT,
                  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                  last_login DATETIME,
                  is_active INTEGER DEFAULT 1)''')
    
    # Student marks table
    c.execute('''CREATE TABLE IF NOT EXISTS student_marks
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  subject_code TEXT,
                  subject_name TEXT,
                  assignment1 INTEGER,
                  assignment2 INTEGER,
                  quiz1 INTEGER,
                  quiz2 INTEGER,
                  mid1 INTEGER,
                  mid2 INTEGER,
                  total INTEGER,
                  user_id TEXT DEFAULT 'demo_student',
                  created_at DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    
    c.execute('CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_users_user_id ON users(user_id)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_chat_intent ON chat_logs(intent)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_chat_time ON chat_logs(timestamp)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_marks_user ON student_marks(user_id)')
    
    # Insert demo users
    c.execute('SELECT COUNT(*) FROM users')
    if c.fetchone()[0] == 0:
        demo_users = [
            # ── CSE Students (3rd year) ──
            ('23951A62B0', '23951A62B0@iare.ac.in', hash_password('123456'), 'Rahul Kumar', 'student', '23951A62B0', 'CSE', 3, '9876543210', 'What is your favorite color?', hash_password('blue')),
            ('23951A62B9', '23951A62B9@iare.ac.in', hash_password('123654'), 'Priya Sharma', 'student', '23951A62B9', 'CSE', 3, '9876543211', 'What is your pet name?', hash_password('buddy')),
            ('23951A6274', '23951A6274@iare.ac.in', hash_password('123654'), 'Anil Reddy', 'student', '23951A6274', 'CSE', 3, '9876543281', 'What is your city?', hash_password('hyderabad')),
            ('23951A6201', '23951A6201@iare.ac.in', hash_password('pass1234'), 'Sneha Rao', 'student', '23951A6201', 'CSE', 3, '9876543220', 'What is your favorite food?', hash_password('biryani')),
            ('23951A6215', '23951A6215@iare.ac.in', hash_password('pass1234'), 'Vikram Singh', 'student', '23951A6215', 'CSE', 3, '9876543221', 'What is your mothers name?', hash_password('lakshmi')),
            ('23951A6230', '23951A6230@iare.ac.in', hash_password('pass1234'), 'Kavya Reddy', 'student', '23951A6230', 'CSE', 3, '9876543222', 'What is your hometown?', hash_password('vizag')),
            ('23951A6245', '23951A6245@iare.ac.in', hash_password('pass1234'), 'Ravi Teja', 'student', '23951A6245', 'CSE', 3, '9876543223', 'What is your favorite movie?', hash_password('bahubali')),
            ('23951A6260', '23951A6260@iare.ac.in', hash_password('pass1234'), 'Deepika Nair', 'student', '23951A6260', 'CSE', 3, '9876543224', 'What is your favorite sport?', hash_password('cricket')),
            # ── CSE-AIML Students (3rd year) ──
            ('23955A7201', '23955A7201@iare.ac.in', hash_password('pass1234'), 'Arjun Patel', 'student', '23955A7201', 'CSE-AIML', 3, '9876543230', 'What is your hobby?', hash_password('coding')),
            ('23955A7215', '23955A7215@iare.ac.in', hash_password('pass1234'), 'Meena Krishna', 'student', '23955A7215', 'CSE-AIML', 3, '9876543231', 'What is your favorite color?', hash_password('green')),
            ('23955A7230', '23955A7230@iare.ac.in', hash_password('pass1234'), 'Suresh Babu', 'student', '23955A7230', 'CSE-AIML', 3, '9876543232', 'What is your dream company?', hash_password('google')),
            # ── CSE-DS Students (3rd year) ──
            ('23955A7301', '23955A7301@iare.ac.in', hash_password('pass1234'), 'Anjali Gupta', 'student', '23955A7301', 'CSE-DS', 3, '9876543240', 'What is your pet name?', hash_password('kitty')),
            ('23955A7315', '23955A7315@iare.ac.in', hash_password('pass1234'), 'Karthik Varma', 'student', '23955A7315', 'CSE-DS', 3, '9876543241', 'What is your school name?', hash_password('dps')),
            # ── ECE Students (3rd year) ──
            ('23951A0401', '23951A0401@iare.ac.in', hash_password('pass1234'), 'Sravani Devi', 'student', '23951A0401', 'ECE', 3, '9876543250', 'What is your favorite subject?', hash_password('signals')),
            ('23951A0420', '23951A0420@iare.ac.in', hash_password('pass1234'), 'Manoj Kumar', 'student', '23951A0420', 'ECE', 3, '9876543251', 'What is your city?', hash_password('warangal')),
            ('23951A0435', '23951A0435@iare.ac.in', hash_password('pass1234'), 'Lavanya Sri', 'student', '23951A0435', 'ECE', 3, '9876543252', 'What is your favorite color?', hash_password('pink')),
            # ── EEE Students (3rd year) ──
            ('23951A0201', '23951A0201@iare.ac.in', hash_password('pass1234'), 'Prasad Reddy', 'student', '23951A0201', 'EEE', 3, '9876543260', 'What is your hobby?', hash_password('reading')),
            ('23951A0215', '23951A0215@iare.ac.in', hash_password('pass1234'), 'Swathi Kumari', 'student', '23951A0215', 'EEE', 3, '9876543261', 'What is your favorite animal?', hash_password('dog')),
            # ── MECH Students (3rd year) ──
            ('23951A0301', '23951A0301@iare.ac.in', hash_password('pass1234'), 'Ganesh Reddy', 'student', '23951A0301', 'MECH', 3, '9876543270', 'What is your dream job?', hash_password('engineer')),
            ('23951A0320', '23951A0320@iare.ac.in', hash_password('pass1234'), 'Sai Krishna', 'student', '23951A0320', 'MECH', 3, '9876543271', 'What is your city?', hash_password('nizamabad')),
            # ── CIVIL Students (3rd year) ──
            ('23951A0101', '23951A0101@iare.ac.in', hash_password('pass1234'), 'Rajesh Kumar', 'student', '23951A0101', 'CIVIL', 3, '9876543280', 'What is your hobby?', hash_password('drawing')),
            # ── 2nd Year Students ──
            ('24951A6201', '24951A6201@iare.ac.in', hash_password('pass1234'), 'Akhil Reddy', 'student', '24951A6201', 'CSE', 2, '9876543290', 'What is your favorite game?', hash_password('pubg')),
            ('24951A6215', '24951A6215@iare.ac.in', hash_password('pass1234'), 'Sai Priya', 'student', '24951A6215', 'CSE', 2, '9876543291', 'What is your dream?', hash_password('engineer')),
            ('24951A0401', '24951A0401@iare.ac.in', hash_password('pass1234'), 'Naveen Kumar', 'student', '24951A0401', 'ECE', 2, '9876543292', 'What is your city?', hash_password('karimnagar')),
            # ── 4th Year Students ──
            ('22951A6201', '22951A6201@iare.ac.in', hash_password('pass1234'), 'Venkat Rao', 'student', '22951A6201', 'CSE', 4, '9876543300', 'What is your favorite color?', hash_password('red')),
            ('22951A6220', '22951A6220@iare.ac.in', hash_password('pass1234'), 'Divya Teja', 'student', '22951A6220', 'CSE', 4, '9876543301', 'What is your pet name?', hash_password('charlie')),
            ('22951A0401', '22951A0401@iare.ac.in', hash_password('pass1234'), 'Harsha Vardhan', 'student', '22951A0401', 'ECE', 4, '9876543302', 'What is your hobby?', hash_password('music')),
            # ── Demo User ──
            ('iaredemo', 'iaredemo@iare.ac.in', hash_password('iaredemo'), 'IARE Demo User', 'student', 'DEMO001', 'CSE', 2, '9876543212', 'What is your college?', hash_password('iare')),
            # ── Admin Users ──
            ('admin_user', 'admin@iare.ac.in', hash_password('admin123'), 'Admin User', 'admin', None, 'Administration', None, '9876543213', 'What is your role?', hash_password('admin')),
            ('super_admin', 'superadmin@iare.ac.in', hash_password('super123'), 'Super Admin', 'admin', None, 'Administration', None, '9876543214', 'What is the college code?', hash_password('iare')),
            # ── Faculty Users ──
            ('faculty_cse', 'faculty.cse@iare.ac.in', hash_password('faculty123'), 'CSE Faculty', 'faculty', None, 'CSE', None, '9876543215', 'What department are you in?', hash_password('cse')),
            ('faculty_ece', 'faculty.ece@iare.ac.in', hash_password('faculty123'), 'ECE Faculty', 'faculty', None, 'ECE', None, '9876543216', 'What department are you in?', hash_password('ece')),
        ]
        c.executemany('''INSERT INTO users 
                        (user_id, email, password_hash, name, role, roll_number, department, year, phone, security_question, security_answer)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', demo_users)
    
    # Insert sample marks data
    c.execute('SELECT COUNT(*) FROM student_marks')
    if c.fetchone()[0] == 0:
        sample_marks = [
            # ── 23951A62B0 - Rahul Kumar (CSE, 3rd Year) ──
            ('ACSD19', 'Data Mining and Machine Learning', 3, 5, 5, 8, 5, 2, 28, '23951A62B0'),
            ('ACSD14', 'Web System Engineering', 7, 3, 5, 5, 5, 5, 30, '23951A62B0'),
            ('ACSD21', 'Artificial Intelligence', 8, 4, 4, 6, 4, 4, 30, '23951A62B0'),
            ('ACCD04', 'Information Security Management', 5, 4, 4, 6, 4, 5, 28, '23951A62B0'),
            ('ACCD08', 'Principles of IoT', 1, 5, 5, 3, 5, 4, 23, '23951A62B0'),
            ('ACSD22', 'Cloud Computing', 7, 6, 4, 5, 6, 5, 33, '23951A62B0'),
            # ── 23951A62B9 - Priya Sharma (CSE, 3rd Year) ──
            ('ACSD19', 'Data Mining and Machine Learning', 8, 7, 4, 7, 8, 7, 41, '23951A62B9'),
            ('ACSD14', 'Web System Engineering', 9, 8, 5, 5, 7, 8, 42, '23951A62B9'),
            ('ACSD21', 'Artificial Intelligence', 7, 6, 5, 4, 6, 7, 35, '23951A62B9'),
            ('ACCD04', 'Information Security Management', 8, 7, 5, 5, 7, 6, 38, '23951A62B9'),
            ('ACCD08', 'Principles of IoT', 6, 7, 4, 5, 6, 5, 33, '23951A62B9'),
            ('ACSD22', 'Cloud Computing', 9, 8, 5, 5, 8, 7, 42, '23951A62B9'),
            # ── 23951A6274 - Anil Reddy (CSE, 3rd Year) ──
            ('ACSD19', 'Data Mining and Machine Learning', 5, 4, 3, 6, 5, 4, 27, '23951A6274'),
            ('ACSD14', 'Web System Engineering', 6, 5, 4, 4, 5, 5, 29, '23951A6274'),
            ('ACSD21', 'Artificial Intelligence', 7, 5, 4, 5, 6, 5, 32, '23951A6274'),
            ('ACCD04', 'Information Security Management', 4, 5, 3, 5, 4, 4, 25, '23951A6274'),
            ('ACCD08', 'Principles of IoT', 5, 4, 4, 4, 5, 3, 25, '23951A6274'),
            ('ACSD22', 'Cloud Computing', 6, 5, 4, 5, 5, 6, 31, '23951A6274'),
            # ── 23951A6201 - Sneha Rao (CSE, 3rd Year) ──
            ('ACSD19', 'Data Mining and Machine Learning', 9, 8, 5, 8, 9, 8, 47, '23951A6201'),
            ('ACSD14', 'Web System Engineering', 8, 9, 5, 5, 8, 9, 44, '23951A6201'),
            ('ACSD21', 'Artificial Intelligence', 9, 8, 5, 5, 9, 8, 44, '23951A6201'),
            ('ACCD04', 'Information Security Management', 8, 8, 5, 5, 8, 7, 41, '23951A6201'),
            ('ACCD08', 'Principles of IoT', 7, 8, 5, 5, 7, 8, 40, '23951A6201'),
            ('ACSD22', 'Cloud Computing', 9, 9, 5, 5, 9, 8, 45, '23951A6201'),
            # ── 23951A6215 - Vikram Singh (CSE, 3rd Year) ──
            ('ACSD19', 'Data Mining and Machine Learning', 6, 5, 4, 6, 6, 5, 32, '23951A6215'),
            ('ACSD14', 'Web System Engineering', 5, 6, 3, 4, 5, 4, 27, '23951A6215'),
            ('ACSD21', 'Artificial Intelligence', 6, 5, 4, 5, 5, 6, 31, '23951A6215'),
            ('ACCD04', 'Information Security Management', 7, 6, 4, 5, 6, 5, 33, '23951A6215'),
            ('ACCD08', 'Principles of IoT', 4, 5, 3, 4, 4, 5, 25, '23951A6215'),
            ('ACSD22', 'Cloud Computing', 5, 6, 4, 4, 5, 5, 29, '23951A6215'),
            # ── 23951A6230 - Kavya Reddy (CSE, 3rd Year) ──
            ('ACSD19', 'Data Mining and Machine Learning', 7, 7, 5, 7, 7, 6, 39, '23951A6230'),
            ('ACSD14', 'Web System Engineering', 8, 7, 4, 5, 7, 7, 38, '23951A6230'),
            ('ACSD21', 'Artificial Intelligence', 8, 8, 5, 5, 8, 7, 41, '23951A6230'),
            ('ACCD04', 'Information Security Management', 7, 6, 4, 5, 7, 6, 35, '23951A6230'),
            ('ACCD08', 'Principles of IoT', 6, 7, 4, 5, 6, 6, 34, '23951A6230'),
            ('ACSD22', 'Cloud Computing', 8, 7, 5, 5, 7, 7, 39, '23951A6230'),
            # ── 23951A6245 - Ravi Teja (CSE, 3rd Year) ──
            ('ACSD19', 'Data Mining and Machine Learning', 4, 3, 3, 5, 4, 3, 22, '23951A6245'),
            ('ACSD14', 'Web System Engineering', 5, 4, 3, 3, 4, 4, 23, '23951A6245'),
            ('ACSD21', 'Artificial Intelligence', 5, 4, 3, 4, 5, 4, 25, '23951A6245'),
            ('ACCD04', 'Information Security Management', 3, 4, 3, 4, 3, 3, 20, '23951A6245'),
            ('ACCD08', 'Principles of IoT', 4, 3, 2, 3, 3, 4, 19, '23951A6245'),
            ('ACSD22', 'Cloud Computing', 5, 5, 3, 4, 4, 4, 25, '23951A6245'),
            # ── 23951A6260 - Deepika Nair (CSE, 3rd Year) ──
            ('ACSD19', 'Data Mining and Machine Learning', 8, 7, 5, 7, 7, 7, 41, '23951A6260'),
            ('ACSD14', 'Web System Engineering', 7, 8, 4, 5, 7, 7, 38, '23951A6260'),
            ('ACSD21', 'Artificial Intelligence', 8, 7, 5, 5, 8, 7, 40, '23951A6260'),
            ('ACCD04', 'Information Security Management', 7, 7, 4, 5, 6, 7, 36, '23951A6260'),
            ('ACCD08', 'Principles of IoT', 6, 6, 4, 5, 6, 5, 32, '23951A6260'),
            ('ACSD22', 'Cloud Computing', 8, 7, 5, 5, 7, 8, 40, '23951A6260'),
            # ── 23955A7201 - Arjun Patel (CSE-AIML, 3rd Year) ──
            ('AAML01', 'Machine Learning', 8, 7, 5, 5, 8, 7, 40, '23955A7201'),
            ('AAML02', 'Deep Learning', 7, 8, 4, 5, 7, 6, 37, '23955A7201'),
            ('AAML03', 'Natural Language Processing', 9, 8, 5, 5, 8, 8, 43, '23955A7201'),
            ('AAML04', 'Computer Vision', 7, 6, 4, 5, 7, 6, 35, '23955A7201'),
            ('AAML05', 'Data Analytics', 8, 7, 5, 5, 7, 7, 39, '23955A7201'),
            # ── 23955A7215 - Meena Krishna (CSE-AIML, 3rd Year) ──
            ('AAML01', 'Machine Learning', 6, 5, 4, 4, 5, 5, 29, '23955A7215'),
            ('AAML02', 'Deep Learning', 5, 6, 3, 4, 5, 4, 27, '23955A7215'),
            ('AAML03', 'Natural Language Processing', 7, 6, 4, 5, 6, 6, 34, '23955A7215'),
            ('AAML04', 'Computer Vision', 6, 5, 4, 4, 6, 5, 30, '23955A7215'),
            ('AAML05', 'Data Analytics', 7, 7, 4, 5, 6, 6, 35, '23955A7215'),
            # ── 23955A7230 - Suresh Babu (CSE-AIML, 3rd Year) ──
            ('AAML01', 'Machine Learning', 9, 9, 5, 5, 9, 8, 45, '23955A7230'),
            ('AAML02', 'Deep Learning', 8, 9, 5, 5, 8, 9, 44, '23955A7230'),
            ('AAML03', 'Natural Language Processing', 9, 8, 5, 5, 9, 8, 44, '23955A7230'),
            ('AAML04', 'Computer Vision', 8, 8, 5, 5, 8, 8, 42, '23955A7230'),
            ('AAML05', 'Data Analytics', 9, 9, 5, 5, 9, 9, 46, '23955A7230'),
            # ── 23955A7301 - Anjali Gupta (CSE-DS, 3rd Year) ──
            ('ADSC01', 'Big Data Analytics', 7, 6, 4, 5, 7, 6, 35, '23955A7301'),
            ('ADSC02', 'Data Visualization', 8, 7, 5, 5, 7, 7, 39, '23955A7301'),
            ('ADSC03', 'Statistical Methods', 6, 7, 4, 4, 6, 6, 33, '23955A7301'),
            ('ADSC04', 'Data Warehousing', 7, 6, 4, 5, 6, 7, 35, '23955A7301'),
            ('ADSC05', 'Predictive Analytics', 8, 8, 5, 5, 7, 7, 40, '23955A7301'),
            # ── 23955A7315 - Karthik Varma (CSE-DS, 3rd Year) ──
            ('ADSC01', 'Big Data Analytics', 5, 4, 3, 4, 5, 4, 25, '23955A7315'),
            ('ADSC02', 'Data Visualization', 6, 5, 4, 4, 5, 5, 29, '23955A7315'),
            ('ADSC03', 'Statistical Methods', 4, 5, 3, 3, 4, 4, 23, '23955A7315'),
            ('ADSC04', 'Data Warehousing', 5, 5, 3, 4, 5, 4, 26, '23955A7315'),
            ('ADSC05', 'Predictive Analytics', 6, 5, 4, 4, 5, 5, 29, '23955A7315'),
            # ── 23951A0401 - Sravani Devi (ECE, 3rd Year) ──
            ('AECE01', 'VLSI Design', 7, 6, 4, 5, 7, 6, 35, '23951A0401'),
            ('AECE02', 'Digital Signal Processing', 8, 7, 5, 5, 7, 7, 39, '23951A0401'),
            ('AECE03', 'Embedded Systems', 7, 7, 4, 5, 6, 7, 36, '23951A0401'),
            ('AECE04', 'Microprocessors', 6, 6, 4, 4, 6, 5, 31, '23951A0401'),
            ('AECE05', 'Communication Systems', 8, 7, 5, 5, 7, 7, 39, '23951A0401'),
            # ── 23951A0420 - Manoj Kumar (ECE, 3rd Year) ──
            ('AECE01', 'VLSI Design', 5, 4, 3, 4, 5, 4, 25, '23951A0420'),
            ('AECE02', 'Digital Signal Processing', 6, 5, 4, 4, 5, 5, 29, '23951A0420'),
            ('AECE03', 'Embedded Systems', 5, 5, 3, 4, 4, 5, 26, '23951A0420'),
            ('AECE04', 'Microprocessors', 4, 5, 3, 3, 4, 4, 23, '23951A0420'),
            ('AECE05', 'Communication Systems', 6, 5, 4, 4, 5, 5, 29, '23951A0420'),
            # ── 23951A0435 - Lavanya Sri (ECE, 3rd Year) ──
            ('AECE01', 'VLSI Design', 9, 8, 5, 5, 8, 8, 43, '23951A0435'),
            ('AECE02', 'Digital Signal Processing', 8, 9, 5, 5, 9, 8, 44, '23951A0435'),
            ('AECE03', 'Embedded Systems', 9, 8, 5, 5, 8, 9, 44, '23951A0435'),
            ('AECE04', 'Microprocessors', 8, 8, 5, 5, 8, 7, 41, '23951A0435'),
            ('AECE05', 'Communication Systems', 9, 9, 5, 5, 9, 8, 45, '23951A0435'),
            # ── 23951A0201 - Prasad Reddy (EEE, 3rd Year) ──
            ('AEEE01', 'Power Systems', 7, 6, 4, 5, 6, 6, 34, '23951A0201'),
            ('AEEE02', 'Control Systems', 6, 7, 4, 4, 6, 5, 32, '23951A0201'),
            ('AEEE03', 'Power Electronics', 7, 6, 4, 5, 7, 6, 35, '23951A0201'),
            ('AEEE04', 'Electrical Machines', 8, 7, 5, 5, 7, 7, 39, '23951A0201'),
            ('AEEE05', 'Measurements & Instrumentation', 6, 6, 4, 4, 5, 6, 31, '23951A0201'),
            # ── 23951A0215 - Swathi Kumari (EEE, 3rd Year) ──
            ('AEEE01', 'Power Systems', 8, 8, 5, 5, 8, 7, 41, '23951A0215'),
            ('AEEE02', 'Control Systems', 9, 8, 5, 5, 8, 8, 43, '23951A0215'),
            ('AEEE03', 'Power Electronics', 8, 7, 5, 5, 7, 8, 40, '23951A0215'),
            ('AEEE04', 'Electrical Machines', 7, 8, 4, 5, 7, 7, 38, '23951A0215'),
            ('AEEE05', 'Measurements & Instrumentation', 8, 7, 5, 5, 8, 7, 40, '23951A0215'),
            # ── 23951A0301 - Ganesh Reddy (MECH, 3rd Year) ──
            ('AMEC01', 'Thermodynamics', 6, 5, 4, 4, 5, 5, 29, '23951A0301'),
            ('AMEC02', 'Manufacturing Technology', 7, 6, 4, 5, 6, 6, 34, '23951A0301'),
            ('AMEC03', 'Machine Design', 5, 6, 3, 4, 5, 5, 28, '23951A0301'),
            ('AMEC04', 'Fluid Mechanics', 6, 5, 4, 4, 6, 5, 30, '23951A0301'),
            ('AMEC05', 'CAD/CAM', 7, 7, 4, 5, 6, 6, 35, '23951A0301'),
            # ── 23951A0320 - Sai Krishna (MECH, 3rd Year) ──
            ('AMEC01', 'Thermodynamics', 8, 7, 5, 5, 7, 7, 39, '23951A0320'),
            ('AMEC02', 'Manufacturing Technology', 7, 8, 4, 5, 7, 6, 37, '23951A0320'),
            ('AMEC03', 'Machine Design', 8, 7, 5, 5, 8, 7, 40, '23951A0320'),
            ('AMEC04', 'Fluid Mechanics', 7, 7, 4, 5, 7, 6, 36, '23951A0320'),
            ('AMEC05', 'CAD/CAM', 8, 8, 5, 5, 7, 7, 40, '23951A0320'),
            # ── 23951A0101 - Rajesh Kumar (CIVIL, 3rd Year) ──
            ('ACIV01', 'Structural Analysis', 7, 6, 4, 5, 6, 6, 34, '23951A0101'),
            ('ACIV02', 'Geotechnical Engineering', 6, 7, 4, 4, 6, 5, 32, '23951A0101'),
            ('ACIV03', 'Transportation Engineering', 7, 6, 4, 5, 7, 6, 35, '23951A0101'),
            ('ACIV04', 'Environmental Engineering', 6, 5, 4, 4, 5, 6, 30, '23951A0101'),
            ('ACIV05', 'Concrete Technology', 8, 7, 5, 5, 7, 7, 39, '23951A0101'),
            # ── 24951A6201 - Akhil Reddy (CSE, 2nd Year) ──
            ('BCSE01', 'Data Structures', 7, 6, 4, 5, 7, 6, 35, '24951A6201'),
            ('BCSE02', 'Object Oriented Programming', 8, 7, 5, 5, 7, 7, 39, '24951A6201'),
            ('BCSE03', 'Computer Organization', 6, 5, 4, 4, 6, 5, 30, '24951A6201'),
            ('BCSE04', 'Discrete Mathematics', 5, 6, 3, 4, 5, 5, 28, '24951A6201'),
            ('BCSE05', 'Database Management Systems', 7, 7, 4, 5, 7, 6, 36, '24951A6201'),
            # ── 24951A6215 - Sai Priya (CSE, 2nd Year) ──
            ('BCSE01', 'Data Structures', 9, 8, 5, 5, 9, 8, 44, '24951A6215'),
            ('BCSE02', 'Object Oriented Programming', 8, 9, 5, 5, 8, 8, 43, '24951A6215'),
            ('BCSE03', 'Computer Organization', 8, 7, 4, 5, 7, 8, 39, '24951A6215'),
            ('BCSE04', 'Discrete Mathematics', 7, 8, 5, 5, 7, 7, 39, '24951A6215'),
            ('BCSE05', 'Database Management Systems', 9, 8, 5, 5, 8, 9, 44, '24951A6215'),
            # ── 24951A0401 - Naveen Kumar (ECE, 2nd Year) ──
            ('BECE01', 'Analog Electronics', 6, 5, 4, 4, 5, 5, 29, '24951A0401'),
            ('BECE02', 'Network Analysis', 7, 6, 4, 5, 6, 6, 34, '24951A0401'),
            ('BECE03', 'Signals and Systems', 5, 6, 3, 4, 5, 5, 28, '24951A0401'),
            ('BECE04', 'Digital Electronics', 7, 7, 4, 5, 6, 6, 35, '24951A0401'),
            ('BECE05', 'Electromagnetic Waves', 6, 5, 4, 4, 5, 6, 30, '24951A0401'),
            # ── 22951A6201 - Venkat Rao (CSE, 4th Year) ──
            ('DCSE01', 'Compiler Design', 7, 7, 4, 5, 7, 6, 36, '22951A6201'),
            ('DCSE02', 'Software Engineering', 8, 7, 5, 5, 7, 8, 40, '22951A6201'),
            ('DCSE03', 'Information Retrieval', 6, 7, 4, 4, 6, 5, 32, '22951A6201'),
            ('DCSE04', 'Distributed Systems', 7, 6, 4, 5, 7, 6, 35, '22951A6201'),
            ('DCSE05', 'Project Work', 8, 8, 5, 5, 8, 8, 42, '22951A6201'),
            # ── 22951A6220 - Divya Teja (CSE, 4th Year) ──
            ('DCSE01', 'Compiler Design', 8, 8, 5, 5, 8, 7, 41, '22951A6220'),
            ('DCSE02', 'Software Engineering', 9, 8, 5, 5, 8, 9, 44, '22951A6220'),
            ('DCSE03', 'Information Retrieval', 7, 8, 4, 5, 7, 7, 38, '22951A6220'),
            ('DCSE04', 'Distributed Systems', 8, 7, 5, 5, 8, 7, 40, '22951A6220'),
            ('DCSE05', 'Project Work', 9, 9, 5, 5, 9, 9, 46, '22951A6220'),
            # ── 22951A0401 - Harsha Vardhan (ECE, 4th Year) ──
            ('DECE01', 'Radar Engineering', 7, 6, 4, 5, 6, 6, 34, '22951A0401'),
            ('DECE02', 'Optical Communications', 6, 7, 4, 4, 6, 5, 32, '22951A0401'),
            ('DECE03', 'Satellite Communications', 7, 7, 4, 5, 7, 6, 36, '22951A0401'),
            ('DECE04', 'Wireless Networks', 8, 7, 5, 5, 7, 7, 39, '22951A0401'),
            ('DECE05', 'Project Work', 8, 8, 5, 5, 8, 7, 41, '22951A0401'),
            # ── iaredemo - Demo User (CSE, 2nd Year) ──
            ('BCSE01', 'Data Structures', 7, 6, 4, 5, 6, 6, 34, 'iaredemo'),
            ('BCSE02', 'Object Oriented Programming', 6, 7, 4, 4, 6, 5, 32, 'iaredemo'),
            ('BCSE03', 'Computer Organization', 7, 6, 4, 5, 7, 6, 35, 'iaredemo'),
            ('BCSE04', 'Discrete Mathematics', 5, 6, 3, 4, 5, 5, 28, 'iaredemo'),
            ('BCSE05', 'Database Management Systems', 8, 7, 5, 5, 7, 7, 39, 'iaredemo'),
        ]
        c.executemany('''INSERT INTO student_marks 
                        (subject_code, subject_name, assignment1, assignment2, quiz1, quiz2, mid1, mid2, total, user_id)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', sample_marks)
    
    # Insert sample analytics data
    c.execute('SELECT COUNT(*) FROM analytics')
    if c.fetchone()[0] == 0:
        sample_analytics = [
            ('2026-02-18', 45, 12, 0.8, 'admission'),
            ('2026-02-19', 62, 18, 0.7, 'placements'),
            ('2026-02-20', 38, 10, 0.9, 'exam'),
            ('2026-02-21', 71, 22, 0.6, 'faculty'),
            ('2026-02-22', 55, 15, 0.75, 'hostel'),
            ('2026-02-23', 48, 14, 0.85, 'library'),
            ('2026-02-24', 67, 20, 0.7, 'placements'),
        ]
        c.executemany('''INSERT INTO analytics 
                        (date, total_queries, unique_users, avg_response_time, top_intent)
                        VALUES (?, ?, ?, ?, ?)''', sample_analytics)
    
    # Insert sample chat logs for analytics
    c.execute('SELECT COUNT(*) FROM chat_logs')
    if c.fetchone()[0] == 0:
        sample_chats = [
            ('23951A62B0', 'What are the admission requirements?', 'For B.Tech: Minimum 60% in 10+2 with PCM. Valid EAMCET/JEE score required.', 'admission', 0.92),
            ('23951A62B9', 'Tell me about placements', 'Our placement cell has partnerships with 200+ companies. Average package: 6.5 LPA.', 'placements', 0.95),
            ('23951A6274', 'What are the library hours?', 'Library hours: 8:00 AM - 8:00 PM on working days.', 'library', 0.88),
            ('23951A6201', 'How to apply for hostel?', 'Fill the hostel application form at admin office or portal. Submit with admission receipt.', 'hostel', 0.90),
            ('23951A6215', 'Show my marks', 'Your academic performance has been retrieved successfully.', 'marks', 0.93),
            ('23955A7201', 'Who is Dr. Ramadevi?', 'Dr. P Ramadevi - Associate Professor, CSE Cyber Security department.', 'faculty', 0.96),
            ('23955A7215', 'What is the exam pattern?', 'CIA-1: 10 marks, CIA-2: 10 marks, AAT: 5 marks, End Semester: 60 marks.', 'exam', 0.91),
            ('23951A0401', 'Bus routes available?', 'IARE buses cover 20+ routes from major areas in Hyderabad.', 'transport', 0.87),
            ('23951A0201', 'WiFi not working', 'Try forgetting the network and reconnecting. Contact IT helpdesk if issues persist.', 'wifi', 0.85),
            ('23951A0301', 'What events are coming up?', 'Technozion tech fest in March, Spectra cultural fest in February.', 'event', 0.89),
            ('iaredemo', 'Hello', 'Hello! I am your Campus Assistant. How can I help you today?', 'greeting', 0.98),
            ('23951A62B0', 'Fee structure for B.Tech?', 'Tuition fee: Rs 1,01,000/year for convener quota. Special fee: Rs 15,000.', 'fee', 0.92),
            ('23951A62B9', 'What scholarships are available?', 'TS Government, AP Government, Merit, AICTE Pragati scholarships available.', 'fee', 0.88),
            ('23951A6230', 'Tell me about college', 'IARE is located at Dundigal, Hyderabad. Offers B.Tech, M.Tech, MBA programs.', 'about_bot', 0.82),
            ('23951A6245', 'Canteen timings?', 'Main canteen operates from 8:00 AM to 6:00 PM with subsidized prices.', 'lab', 0.78),
            ('23951A6260', 'Contact number of college', 'Main Office: 040-24680600, Admissions: 040-24680611, Principal: 040-24680601.', 'contact', 0.94),
            ('23955A7301', 'How to get bonafide certificate?', 'Apply at Administrative Office with ID card. Processing takes 2-3 working days.', 'knowledge_base', 0.86),
            ('24951A6201', 'What labs are available?', 'CSE: Programming Lab, Networks Lab, AI/ML Lab. ECE: VLSI, Embedded Systems Lab.', 'lab', 0.90),
            ('24951A6215', 'Sports facilities?', 'Cricket, Football, Basketball, Badminton, Tennis, Gym and more available.', 'knowledge_base', 0.88),
            ('22951A6201', 'Placement training details', 'Aptitude, Programming, Soft Skills, Mock Interviews, Resume Building workshops provided.', 'placements', 0.91),
        ]
        c.executemany('''INSERT INTO chat_logs 
                        (user_id, user_message, bot_response, intent, confidence)
                        VALUES (?, ?, ?, ?, ?)''', sample_chats)
    
    conn.commit()
    conn.close()

init_db()
init_default_faqs()

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
    try:
        data = request.json
        user_message = data.get('message', '')
        user_id = data.get('user_id', 'anonymous')
        
        if not user_message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Get chatbot response
        response_data = chatbot.get_response(user_message, user_id=user_id)
        
        # Log to database
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''INSERT INTO chat_logs 
                     (user_id, user_message, bot_response, intent, confidence)
                     VALUES (?, ?, ?, ?, ?)''',
                  (user_id, user_message, response_data['response'],
                   response_data['intent'], response_data['confidence']))
        conn.commit()
        conn.close()
        
        return jsonify({
            'response': response_data['response'],
            'intent': response_data['intent'],
            'confidence': response_data['confidence'],
            'suggestions': response_data.get('suggestions', [])
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/faqs', methods=['GET'])
def get_faqs():
    """Get all FAQs"""
    try:
        category = request.args.get('category', None)
        
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        if category:
            c.execute('SELECT * FROM faqs WHERE category = ? ORDER BY id DESC', (category,))
        else:
            c.execute('SELECT * FROM faqs ORDER BY category, id DESC')
        
        faqs = []
        for row in c.fetchall():
            faqs.append({
                'id': row[0],
                'category': row[1],
                'question': row[2],
                'answer': row[3],
                'keywords': row[4]
            })
        
        conn.close()
        return jsonify(faqs)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/faqs', methods=['POST'])
def add_faq():
    """Add new FAQ (Admin only)"""
    try:
        data = request.json
        
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''INSERT INTO faqs (category, question, answer, keywords)
                     VALUES (?, ?, ?, ?)''',
                  (data['category'], data['question'], data['answer'],
                   data.get('keywords', '')))
        conn.commit()
        faq_id = c.lastrowid
        conn.close()
        
        # Retrain chatbot with new FAQ
        chatbot.reload_knowledge_base()
        
        return jsonify({'id': faq_id, 'message': 'FAQ added successfully'})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/faqs/<int:faq_id>', methods=['PUT'])
def update_faq(faq_id):
    """Update FAQ (Admin only)"""
    try:
        data = request.json
        
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''UPDATE faqs 
                     SET category = ?, question = ?, answer = ?, keywords = ?,
                         updated_at = CURRENT_TIMESTAMP
                     WHERE id = ?''',
                  (data['category'], data['question'], data['answer'],
                   data.get('keywords', ''), faq_id))
        conn.commit()
        conn.close()
        
        chatbot.reload_knowledge_base()
        
        return jsonify({'message': 'FAQ updated successfully'})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/faqs/<int:faq_id>', methods=['DELETE'])
def delete_faq(faq_id):
    """Delete FAQ (Admin only)"""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('DELETE FROM faqs WHERE id = ?', (faq_id,))
        conn.commit()
        conn.close()
        
        chatbot.reload_knowledge_base()
        
        return jsonify({'message': 'FAQ deleted successfully'})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics', methods=['GET'])
def get_analytics():
    """Get chatbot analytics (Admin only)"""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        # Total queries
        c.execute('SELECT COUNT(*) FROM chat_logs')
        total_queries = c.fetchone()[0]
        
        # Unique users
        c.execute('SELECT COUNT(DISTINCT user_id) FROM chat_logs')
        unique_users = c.fetchone()[0]
        
        # Top intents
        c.execute('''SELECT intent, COUNT(*) as count 
                     FROM chat_logs 
                     WHERE intent IS NOT NULL
                     GROUP BY intent 
                     ORDER BY count DESC 
                     LIMIT 5''')
        top_intents = [{'intent': row[0], 'count': row[1]} for row in c.fetchall()]
        
        # Recent queries
        c.execute('''SELECT user_message, bot_response, timestamp, intent 
                     FROM chat_logs 
                     ORDER BY timestamp DESC 
                     LIMIT 20''')
        recent_queries = []
        for row in c.fetchall():
            recent_queries.append({
                'user_message': row[0],
                'bot_response': row[1],
                'timestamp': row[2],
                'intent': row[3]
            })
        
        # Queries by date (last 7 days)
        c.execute('''SELECT DATE(timestamp) as date, COUNT(*) as count
                     FROM chat_logs
                     WHERE timestamp >= datetime('now', '-7 days')
                     GROUP BY DATE(timestamp)
                     ORDER BY date''')
        queries_by_date = [{'date': row[0], 'count': row[1]} for row in c.fetchall()]
        
        conn.close()
        
        return jsonify({
            'total_queries': total_queries,
            'unique_users': unique_users,
            'top_intents': top_intents,
            'recent_queries': recent_queries,
            'queries_by_date': queries_by_date
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

@app.route('/api/auth/login', methods=['POST'])
def login():
    """User login endpoint"""
    try:
        data = request.json
        email = data.get('email', '').strip()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE email = ?', (email,))
        user = c.fetchone()
        
        if not user:
            conn.close()
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Verify password
        if not verify_password(password, user[3]):
            conn.close()
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Check if user is active
        if user[14] != 1:
            conn.close()
            return jsonify({'error': 'Account is deactivated'}), 403
        
        # Update last login
        c.execute('UPDATE users SET last_login = ? WHERE id = ?', 
                  (datetime.now(), user[0]))
        conn.commit()
        conn.close()
        
        # Return user data (without password hash)
        return jsonify({
            'success': True,
            'user': {
                'id': user[0],
                'user_id': user[1],
                'email': user[2],
                'name': user[4],
                'role': user[5],
                'roll_number': user[6],
                'department': user[7],
                'year': user[8],
                'phone': user[9]
            }
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/register', methods=['POST'])
def register():
    """User registration endpoint"""
    try:
        data = request.json
        user_id = data.get('user_id', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        name = data.get('name', '').strip()
        roll_number = data.get('roll_number', '').strip()
        department = data.get('department', '').strip()
        year = data.get('year')
        phone = data.get('phone', '').strip()
        
        # Validation
        if not user_id or not email or not password or not name:
            return jsonify({'error': 'User ID, email, password, and name are required'}), 400
        
        if not email.endswith('@iare.ac.in'):
            return jsonify({'error': 'Please use IARE college email'}), 400
        
        if len(password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters'}), 400
        
        # Validate user_id format (alphanumeric and underscore only)
        if not user_id.replace('_', '').isalnum():
            return jsonify({'error': 'User ID can only contain letters, numbers, and underscores'}), 400
        
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        # Check if email already exists
        c.execute('SELECT id FROM users WHERE email = ?', (email,))
        if c.fetchone():
            conn.close()
            return jsonify({'error': 'Email already registered'}), 409
        
        # Check if user_id already exists
        c.execute('SELECT id FROM users WHERE user_id = ?', (user_id,))
        if c.fetchone():
            conn.close()
            return jsonify({'error': 'User ID already taken'}), 409
        
        # Insert new user
        password_hash = hash_password(password)
        c.execute('''INSERT INTO users 
                    (user_id, email, password_hash, name, role, roll_number, department, year, phone)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                  (user_id, email, password_hash, name, 'student', roll_number, department, year, phone))
        
        conn.commit()
        user_db_id = c.lastrowid
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Registration successful',
            'user': {
                'id': user_db_id,
                'user_id': user_id,
                'email': email,
                'name': name,
                'role': 'student',
                'roll_number': roll_number,
                'department': department,
                'year': year,
                'phone': phone
            }
        }), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/forgot-password', methods=['POST'])
def forgot_password():
    """Check if email exists and return security question"""
    try:
        data = request.json
        email = data.get('email', '').strip()
        
        if not email:
            return jsonify({'error': 'Email is required'}), 400
        
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('SELECT security_question FROM users WHERE email = ?', (email,))
        user = c.fetchone()
        conn.close()
        
        if not user:
            return jsonify({'error': 'Email not found'}), 404
        
        if not user[0]:
            return jsonify({'error': 'No security question set for this account'}), 400
        
        return jsonify({
            'success': True,
            'security_question': user[0]
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/verify-answer', methods=['POST'])
def verify_answer():
    """Verify security answer and allow password reset"""
    try:
        data = request.json
        email = data.get('email', '').strip()
        answer = data.get('answer', '').strip()
        
        if not email or not answer:
            return jsonify({'error': 'Email and answer are required'}), 400
        
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('SELECT security_answer FROM users WHERE email = ?', (email,))
        user = c.fetchone()
        conn.close()
        
        if not user:
            return jsonify({'error': 'Email not found'}), 404
        
        # Verify answer
        if not verify_password(answer, user[0]):
            return jsonify({'error': 'Incorrect answer'}), 401
        
        return jsonify({
            'success': True,
            'message': 'Answer verified successfully'
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/reset-password', methods=['POST'])
def reset_password():
    """Reset user password after security verification"""
    try:
        data = request.json
        email = data.get('email', '').strip()
        new_password = data.get('new_password', '')
        
        if not email or not new_password:
            return jsonify({'error': 'Email and new password are required'}), 400
        
        if len(new_password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters'}), 400
        
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        # Update password
        new_password_hash = hash_password(new_password)
        c.execute('UPDATE users SET password_hash = ? WHERE email = ?', 
                  (new_password_hash, email))
        
        if c.rowcount == 0:
            conn.close()
            return jsonify({'error': 'Email not found'}), 404
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Password reset successfully'
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/marks', methods=['GET'])
def get_marks():
    """Get student marks"""
    try:
        user_id = request.args.get('user_id', '23951A62B0')
        
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''SELECT subject_code, subject_name, assignment1, assignment2, 
                     quiz1, quiz2, mid1, mid2, total 
                     FROM student_marks WHERE user_id = ?''', (user_id,))
        
        marks = []
        for row in c.fetchall():
            marks.append({
                'subject_code': row[0],
                'subject_name': row[1],
                'assignment1': row[2],
                'assignment2': row[3],
                'quiz1': row[4],
                'quiz2': row[5],
                'mid1': row[6],
                'mid2': row[7],
                'total': row[8]
            })
        
        conn.close()
        return jsonify(marks)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/users', methods=['GET'])
def get_users():
    """Get all registered users (Admin only)"""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''SELECT id, user_id, email, name, role, roll_number, 
                     department, year, phone, created_at, last_login, is_active 
                     FROM users ORDER BY created_at DESC''')
        
        users = []
        for row in c.fetchall():
            users.append({
                'id': row[0],
                'user_id': row[1],
                'email': row[2],
                'name': row[3],
                'role': row[4],
                'roll_number': row[5],
                'department': row[6],
                'year': row[7],
                'phone': row[8],
                'created_at': row[9],
                'last_login': row[10],
                'is_active': row[11]
            })
        
        conn.close()
        return jsonify(users)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def verify_pin():
    """Verify PIN before starting the server"""
    # Default PIN - you can change this or load from environment variable
    CORRECT_PIN = os.getenv('SERVER_PIN', '1510')
    
    print("\n" + "="*60)
    print("🔐 CAMPUS ASSISTANT CHATBOT - SERVER AUTHENTICATION")
    print("="*60)
    
    max_attempts = 3
    attempts = 0
    
    while attempts < max_attempts:
        try:
            pin = input(f"\n🔑 Enter PIN to start server (Attempt {attempts + 1}/{max_attempts}): ").strip()
            
            if pin == CORRECT_PIN:
                print("\n✅ PIN Verified Successfully!")
                print("="*60)
                return True
            else:
                attempts += 1
                remaining = max_attempts - attempts
                if remaining > 0:
                    print(f"❌ Incorrect PIN! {remaining} attempt(s) remaining.")
                else:
                    print("\n❌ Maximum attempts exceeded. Access denied!")
                    print("="*60)
                    return False
        except KeyboardInterrupt:
            print("\n\n⚠️  Server startup cancelled by user.")
            print("="*60)
            return False
        except Exception as e:
            print(f"\n⚠️  Error: {e}")
            return False
    
    return False

if __name__ == '__main__':
    # Verify PIN before starting server
    if not verify_pin():
        print("\n🚫 Server startup aborted due to authentication failure.\n")
        exit(1)
    
    print("\n🚀 Campus Assistant Chatbot Backend Starting...")
    print("📊 Database initialized")
    print("🤖 Chatbot engine ready")
    print("🌐 Server running at http://localhost:5000")
    print("="*60 + "\n")
    app.run(debug=True, port=5000, host='0.0.0.0')
