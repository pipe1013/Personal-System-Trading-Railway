import os
import sqlite3
from flask import Flask, render_template, redirect, url_for, request, session, flash, jsonify
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import numpy as np
import websocket
from config import DB_PATH
from utils.data_fetcher import obtener_datos_indice_vivo
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)

# Production-ready secret key handling
app.secret_key = os.getenv('SECRET_KEY', 'your_secret_key')

# CSRF protection
csrf = CSRFProtect(app)

# Configuración de la carpeta de carga
UPLOAD_FOLDER = 'static/uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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

        # Crea la tabla trades
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                notebook_id INTEGER,
                asset TEXT NOT NULL,
                account_balance REAL,
                account_type TEXT CHECK(account_type IN ('Demo', 'Real')),
                lot_size REAL NOT NULL,
                entry_point REAL NOT NULL,
                stop_loss REAL,
                take_profit REAL,
                result TEXT CHECK(result IN ('Ganadora', 'Perdedora')),
                trade_date DATE,
                emotion TEXT CHECK(emotion IN ('Confianza', 'Ansiedad', 'Optimismo', 'Miedo', 'Euforia', 'Irritación', 'Calma')),
                activation_routine BOOLEAN,
                entry_image_path TEXT,
                FOREIGN KEY (notebook_id) REFERENCES notebooks(id),
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')

        # Crea la tabla users
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
            )
        ''')

        # Crea la tabla notebooks
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notebooks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                initial_balance REAL,
                account_type TEXT CHECK(account_type IN ('Demo', 'Real')),
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')

        # Crea la tabla personal_notebooks
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS personal_notebooks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                content TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')

        # Crea la tabla pages
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                personal_notebook_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                content TEXT,
                FOREIGN KEY (personal_notebook_id) REFERENCES personal_notebooks(id)
            )
        ''')

        # Crea la tabla habitos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS habitos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                mes TEXT NOT NULL,
                habito TEXT NOT NULL,
                dia INTEGER NOT NULL,
                cumplido BOOLEAN NOT NULL DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')

        # Crea la tabla capital_history
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS capital_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                notebook_id INTEGER NOT NULL,
                trade_date DATE NOT NULL,
                capital REAL NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (notebook_id) REFERENCES notebooks(id)
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
    if 'user_id' in session:
        username = session.get('username')
        welcome_message = session.pop('welcome', None)
        return render_template('base.html', username=username, welcome_message=welcome_message, show_video=True)
    return redirect(url_for('login'))

# Add a simple test route
@app.route('/test')
def test():
    return "Flask app is running!"

if __name__ == '__main__':
    # Configure for production
    port = int(os.getenv('PORT', 5000))
    debug = not bool(os.getenv('RAILWAY_ENVIRONMENT'))
    
    app.run(host='0.0.0.0', port=port, debug=debug)
