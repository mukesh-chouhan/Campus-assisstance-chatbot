import sqlite3
import hashlib

def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

# Connect to database
conn = sqlite3.connect('campus_assistant.db')
c = conn.cursor()

# Check if users table exists
c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
if c.fetchone():
    print("✅ Users table exists\n")
    
    # Get all users
    c.execute('SELECT user_id, email, name, role FROM users')
    users = c.fetchall()
    
    print(f"Total users: {len(users)}\n")
    for user in users:
        print(f"User ID: {user[0]}")
        print(f"Email: {user[1]}")
        print(f"Name: {user[2]}")
        print(f"Role: {user[3]}")
        print("-" * 50)
    
    # Check specific user
    print("\n🔍 Checking for 23951A62B0@iare.ac.in...")
    c.execute('SELECT * FROM users WHERE email = ?', ('23951A62B0@iare.ac.in',))
    user = c.fetchone()
    
    if user:
        print("✅ User found!")
        print(f"User ID: {user[1]}")
        print(f"Email: {user[2]}")
        print(f"Name: {user[4]}")
        
        # Verify password
        test_password = '123456'
        stored_hash = user[3]
        test_hash = hash_password(test_password)
        
        if stored_hash == test_hash:
            print(f"✅ Password '123456' is correct!")
        else:
            print(f"❌ Password '123456' does NOT match!")
            print(f"Stored hash: {stored_hash[:20]}...")
            print(f"Test hash: {test_hash[:20]}...")
    else:
        print("❌ User NOT found!")
        print("\n💡 Adding user now...")
        c.execute('''INSERT INTO users 
                    (user_id, email, password_hash, name, role, roll_number, department, year, phone)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                  ('23951A62B0', '23951A62B0@iare.ac.in', hash_password('123456'), 
                   'Demo Student', 'student', '23951A62B0', 'CSE', 3, '9876543210'))
        conn.commit()
        print("✅ User added successfully!")
        
else:
    print("❌ Users table does NOT exist!")

conn.close()
