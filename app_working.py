import os
import sqlite3
from flask import Flask, render_template, redirect, url_for, request, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from config import DB_PATH
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)

# Production-ready secret key handling
app.secret_key = os.getenv('SECRET_KEY', 'your_secret_key')

# CSRF protection
csrf = CSRFProtect(app)

def get_db_connection():
    connection = sqlite3.connect(DB_PATH, timeout=30)
    connection.row_factory = sqlite3.Row
    return connection

# Initialize database function
def init_db():
    """Initialize the database with required tables"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
            )
        ''')

        # Create notebooks table
        cursor.execute('''
            CREATE TABLE IF NOT NOT EXISTS notebooks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                initial_balance REAL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')

        connection.commit()
        connection.close()
        print("Database initialized successfully.")
    except Exception as e:
        print(f"Error initializing database: {e}")

# Initialize database on startup
init_db()

@app.route('/')
def home():
    return "Trading System Running!"

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        connection.close()
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.', 'error')
    
    return "Login page - create your login.html template"

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if len(password) < 4:
            flash('Password must be at least 4 characters.', 'error')
            return redirect(url_for('register'))
        
        hashed_password = generate_password_hash(password)
        
        connection = get_db_connection()
        cursor = connection.cursor()
        try:
            cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
            connection.commit()
            flash('User created successfully! Please log in.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username already exists. Try a different one.', 'error')
            return redirect(url_for('register'))
        finally:
            connection.close()
    
    return "Register page - create your register.html template"

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return "Dashboard - Welcome to Trading System!"

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    flash('Logged out successfully!')
    return redirect(url_for('login'))

@app.route('/test')
def test():
    return "Flask trading system is running!"

if __name__ == '__main__':
    # Configure for production
    port = int(os.getenv('PORT', 5000))
    debug = not bool(os.getenv('RAILWAY_ENVIRONMENT'))
    
    app.run(host='0.0.0.0', port=port, debug=debug)
