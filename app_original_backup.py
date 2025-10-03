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

# Production-ready database connection function
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

# Initialize database function
def init_db():
    """Initialize the database with required tables"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # Crea la tabla trades con todas las columnas necesarias
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

def init_db():
    """Initialize the database with required tables"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # Crea la tabla trades con todas las columnas necesarias
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

        # Crea la tabla personal_notebooks con la columna "content" para almacenar las notas
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

        # Crea la tabla capital_history para análisis de drawdown
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
        print("Database initialized systematically.")
    except Exception as e:
        print(f"Error initializing database: {e}")

# Initialize database on app startup
init_db()

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if len(password) < 4:
            flash('La contraseña debe tener al menos 4 caracteres.', 'error')
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password)

        connection = get_db_connection()
        cursor = connection.cursor()
        try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # Crea la tabla trades con todas las columnas necesarias
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
        
        # Crea la tabla personal_notebooks con la columna "content" para almacenar las notas
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
        
        # Crea la tabla capital_history para análisis de drawdown
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

@app.route('/')
def home():
    if 'user_id' in session:
        username = session.get('username')
        welcome_message = session.pop('welcome', None)
        return render_template('base.html', username=username, welcome_message=welcome_message, show_video=True)
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if len(password) < 4:
            flash('La contraseña debe tener al menos 4 caracteres.', 'error')
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

    return render_template('auth/register.html')

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
            session['welcome'] = f'Bienvenido, {username}!'
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password.', 'login_error')

    return render_template('auth/login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    flash('Logged out successfully!')
    return redirect(url_for('login'))

@app.route('/create_notebook', methods=['POST'])
def create_notebook():
    if 'user_id' not in session:
        return jsonify({"error": "Please log in to create a notebook."}), 403

    user_id = session['user_id']
    name = request.form['name']
    initial_balance = request.form['initial_balance']
    account_type = request.form['account_type']

    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('INSERT INTO notebooks (user_id, name, initial_balance, account_type) VALUES (?, ?, ?, ?)',
                   (user_id, name, initial_balance, account_type))
    connection.commit()
    notebook_id = cursor.lastrowid
    connection.close()

    return jsonify({"id": notebook_id, "name": name, "initial_balance": initial_balance, "account_type": account_type})

@app.route('/register_trade', methods=['GET', 'POST'])
def register_trade():
    if 'user_id' not in session:
        flash('Please log in to access this page.')
        return redirect(url_for('login'))

    connection = get_db_connection()
    cursor = connection.cursor()

    if request.method == 'POST':
        # Obtener datos del formulario
        user_id = session['user_id']
        notebook_id = request.form['notebook_id']
        asset = request.form['asset']
        lot_size = request.form['lot_size']
        entry_point = request.form['entry_point']
        stop_loss = request.form['stop_loss']
        take_profit = request.form['take_profit']
        result = request.form['result']
        trade_date = request.form['trade_date']
        emotion = request.form['emotion']
        activation_routine = request.form.get('activation_routine') == 'yes'
        entry_image = request.files['entry_image']

        # Guardar imagen si se proporciona
        entry_image_path = None
        if entry_image and entry_image.filename != '':
            entry_image_filename = secure_filename(entry_image.filename)
            entry_image_path = os.path.join(app.config['UPLOAD_FOLDER'], entry_image_filename)
            entry_image.save(entry_image_path)

        # Insertar datos en la base de datos, incluyendo user_id
        cursor.execute('''INSERT INTO trades (user_id, notebook_id, asset, lot_size, entry_point, 
                        stop_loss, take_profit, result, trade_date, emotion, activation_routine, entry_image_path)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                       (user_id, notebook_id, asset, lot_size, entry_point, stop_loss, take_profit, result,
                        trade_date, emotion, activation_routine, entry_image_path))
        connection.commit()
        connection.close()

        flash('Trade registrado exitosamente.')
        return redirect(url_for('home'))

    # Obtener cuadernos para el selector
    cursor.execute('SELECT * FROM notebooks WHERE user_id = ?', (session['user_id'],))
    notebooks = cursor.fetchall()
    connection.close()

    return render_template('register_trade.html', notebooks=notebooks)

@app.route('/estadisticas')
def estadisticas():
    connection = get_db_connection()
    cursor = connection.cursor()

    # Obtener información de los cuadernos para el selector
    cursor.execute("SELECT * FROM notebooks WHERE user_id = ?", (session['user_id'],))
    notebooks = cursor.fetchall()

    # Obtener los meses disponibles con trades
    cursor.execute("""
        SELECT DISTINCT strftime('%Y-%m', trade_date) as month
        FROM trades
        WHERE user_id = ?
        ORDER BY month DESC
    """, (session['user_id'],))
    months = [row['month'] for row in cursor.fetchall()]
    
    connection.close()

    return render_template('estadisticas.html', notebooks=notebooks, months=months, notebook_id=None)

@app.route('/obtener_meses', methods=['GET'])
def obtener_meses():
    notebook_id = request.args.get('notebook_id')

    if not notebook_id:
        return jsonify({"error": "No se proporcionó el ID del cuaderno"}), 400

    connection = get_db_connection()
    cursor = connection.cursor()

    # Obtener los meses disponibles con trades para el cuaderno seleccionado
    cursor.execute("""
        SELECT DISTINCT strftime('%Y-%m', trade_date) as month
        FROM trades
        WHERE user_id = ? AND notebook_id = ?
        ORDER BY month DESC
    """, (session['user_id'], notebook_id))
    months = cursor.fetchall()
    connection.close()

    # Convertir los resultados en una lista de strings
    months_list = [row["month"] for row in months]

    return jsonify({"months": months_list})

@app.route('/cargar_datos_estadisticas', methods=['GET'])
def cargar_datos_estadisticas():
    notebook_id = request.args.get('notebook_id')
    mes = request.args.get('mes')

    if not notebook_id or not mes:
        return jsonify({"error": "No se proporcionó el ID del cuaderno o el mes"}), 400

    connection = get_db_connection()
    cursor = connection.cursor()

    # Obtener capital inicial del cuaderno seleccionado
    cursor.execute("SELECT initial_balance FROM notebooks WHERE id = ? AND user_id = ?", (notebook_id, session['user_id']))
    notebook = cursor.fetchone()
    if not notebook:
        return jsonify({"error": "No se encontró el cuaderno seleccionado"}), 404

    initial_balance = notebook["initial_balance"]

    # Cálculo del capital en cuenta en base a cada trade, de forma acumulativa
    cursor.execute("""
        SELECT trade_date, result, entry_point, stop_loss, take_profit, lot_size, asset
        FROM trades
        WHERE notebook_id = ? AND user_id = ? AND strftime('%Y-%m', trade_date) = ?
        ORDER BY trade_date
    """, (notebook_id, session['user_id'], mes))
    
    trades = cursor.fetchall()
    dates = []
    capital = []

    # Agregar el saldo inicial como el primer punto del gráfico
    dates.append("Inicio")
    capital.append(initial_balance)

    # Continuar con las operaciones acumulativas
    current_balance = initial_balance
    for trade in trades:
        asset = trade["asset"].lower()
        lot_size = trade["lot_size"]
        entry_point = trade["entry_point"]
        take_profit = trade["take_profit"]
        stop_loss = trade["stop_loss"]

        # Ajustar las ganancias o pérdidas en función del tipo de índice y del tamaño del pip
        if "boom" in asset:  # Boom - Solo Compras
            if trade["result"] == "Ganadora":
                gain = (take_profit - entry_point) * lot_size
                current_balance += gain
            elif trade["result"] == "Perdedora":
                loss = (entry_point - stop_loss) * lot_size
                current_balance -= loss
        elif "crash" in asset:  # Crash - Solo Ventas
            if trade["result"] == "Ganadora":
                gain = (entry_point - take_profit) * lot_size
                current_balance += gain
            elif trade["result"] == "Perdedora":
                loss = (stop_loss - entry_point) * lot_size
                current_balance -= loss

        dates.append(trade["trade_date"])
        capital.append(current_balance)

    performance_data = {
        "dates": dates,
        "capital": capital
    }

    # Otros cálculos estadísticos
    cursor.execute("""
        SELECT result, COUNT(*) as count
        FROM trades
        WHERE user_id = ? AND notebook_id = ? AND strftime('%Y-%m', trade_date) = ?
        GROUP BY result
    """, (session['user_id'], notebook_id, mes))
    result_counts = cursor.fetchall()
    results_distribution = {
        "wins": sum(row["count"] for row in result_counts if row["result"] == "Ganadora"),
        "losses": sum(row["count"] for row in result_counts if row["result"] == "Perdedora")
    }

    cursor.execute("""
        SELECT 
            AVG(CASE WHEN result = 'Ganadora' AND asset LIKE 'boom%' THEN (take_profit - entry_point) * lot_size
                     WHEN result = 'Ganadora' AND asset LIKE 'crash%' THEN (entry_point - take_profit) * lot_size
                     ELSE NULL END) AS avg_gain,
            AVG(CASE WHEN result = 'Perdedora' AND asset LIKE 'boom%' THEN (entry_point - stop_loss) * lot_size
                     WHEN result = 'Perdedora' AND asset LIKE 'crash%' THEN (stop_loss - entry_point) * lot_size
                     ELSE NULL END) AS avg_loss
        FROM trades
        WHERE user_id = ? AND notebook_id = ? AND strftime('%Y-%m', trade_date) = ?
    """, (session['user_id'], notebook_id, mes))
    avg_data = cursor.fetchone()
    average_win_loss = {
        "avg_win": avg_data["avg_gain"] if avg_data["avg_gain"] is not None else 0,
        "avg_loss": avg_data["avg_loss"] if avg_data["avg_loss"] is not None else 0
    }

    cursor.execute("""
        SELECT strftime('%W', trade_date) AS week, SUM((CASE 
            WHEN result = 'Ganadora' AND asset LIKE 'boom%' THEN (take_profit - entry_point)
            WHEN result = 'Ganadora' AND asset LIKE 'crash%' THEN (entry_point - take_profit)
            WHEN result = 'Perdedora' AND asset LIKE 'boom%' THEN (entry_point - stop_loss) * -1
            WHEN result = 'Perdedora' AND asset LIKE 'crash%' THEN (stop_loss - entry_point) * -1
            END) * lot_size) AS profit
        FROM trades
        WHERE user_id = ? AND notebook_id = ? AND strftime('%Y-%m', trade_date) = ?
        GROUP BY week
    """, (session['user_id'], notebook_id, mes))
    weekly_performance_data = cursor.fetchall()
    weekly_performance = {
        "weeks": [row["week"] for row in weekly_performance_data],
        "profits": [row["profit"] for row in weekly_performance_data]
    }

    cursor.execute("""
        SELECT emotion, 
               COUNT(*) AS total, 
               ROUND(SUM(CASE WHEN result = 'Ganadora' THEN 1 ELSE 0 END) * 1.0 / COUNT(*), 2) AS success_rate
        FROM trades
        WHERE user_id = ? AND notebook_id = ? AND strftime('%Y-%m', trade_date) = ?
        GROUP BY emotion
    """, (session['user_id'], notebook_id, mes))
    emotion_data = cursor.fetchall()
    emotion_performance = {
        "emotions": [row["emotion"] for row in emotion_data],
        "success_rates": [row["success_rate"] for row in emotion_data]
    }

    # Nuevo cálculo: Activo más operado
    cursor.execute("""
        SELECT asset, COUNT(*) as total
        FROM trades
        WHERE user_id = ? AND notebook_id = ? AND strftime('%Y-%m', trade_date) = ?
        GROUP BY asset
        ORDER BY total DESC
    """, (session['user_id'], notebook_id, mes))
    asset_data = cursor.fetchall()
    asset_distribution = {
        "assets": [row["asset"] for row in asset_data],
        "counts": [row["total"] for row in asset_data]
    }

    connection.close()

    # Devolver datos como JSON
    data = {
        "performance_data": performance_data,
        "results_distribution": results_distribution,
        "average_win_loss": average_win_loss,
        "weekly_performance": weekly_performance,
        "emotion_performance": emotion_performance,
        "asset_distribution": asset_distribution,
    }

    print("Datos enviados al frontend:", data)
    
    return jsonify(data)

# Historial de cuadernos y trades
from flask import Flask, render_template, request, jsonify, session, send_from_directory, send_file
import sqlite3
import os
import pandas as pd
from datetime import datetime
from flask import redirect, url_for

# Historial de cuadernos y trades
@app.route('/historial')
def historial():
    connection = get_db_connection()
    cursor = connection.cursor()

    # Obtener todos los cuadernos para el selector de filtro
    cursor.execute("SELECT * FROM notebooks WHERE user_id = ?", (session['user_id'],))
    notebooks = cursor.fetchall()
    connection.close()

    return render_template('historial.html', notebooks=notebooks)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory('static/uploads', filename)

@app.route('/cargar_historial', methods=['GET'])
def cargar_historial():
    notebook_id = request.args.get('notebook_id')

    connection = get_db_connection()
    cursor = connection.cursor()

    # Consulta para obtener los trades según el filtro de cuaderno
    if notebook_id:
        cursor.execute("""
            SELECT t.*, n.name as notebook_name
            FROM trades t
            JOIN notebooks n ON t.notebook_id = n.id
            WHERE t.user_id = ? AND t.notebook_id = ?
            ORDER BY t.trade_date DESC
        """, (session['user_id'], notebook_id))
    else:
        cursor.execute("""
            SELECT t.*, n.name as notebook_name
            FROM trades t
            JOIN notebooks n ON t.notebook_id = n.id
            WHERE t.user_id = ?
            ORDER BY t.trade_date DESC
        """, (session['user_id'],))

    trades = cursor.fetchall()
    connection.close()

    trade_list = []
    for trade in trades:
        # Calcular ganancia/pérdida
        if trade['result'] == 'Ganadora':
            profit_loss = abs((trade['take_profit'] - trade['entry_point']) * trade['lot_size']) if 'Boom' in trade['asset'] else abs((trade['entry_point'] - trade['take_profit']) * trade['lot_size'])
        elif trade['result'] == 'Perdedora':
            profit_loss = abs((trade['entry_point'] - trade['stop_loss']) * trade['lot_size']) if 'Boom' in trade['asset'] else abs((trade['stop_loss'] - trade['entry_point']) * trade['lot_size'])
        else:
            profit_loss = 0

        profit_loss_display = f"{profit_loss} USD"

        entry_image_path = trade["entry_image_path"]
        print("Ruta original en la BD:", entry_image_path)  # Para depuración

        if entry_image_path:
            # Normalizamos la ruta reemplazando backslashes por slashes
            entry_image_path = entry_image_path.replace("\\", "/")

            # Ahora removemos el prefijo si existe
            prefix = "static/uploads/"
            if entry_image_path.startswith(prefix):
                entry_image_path = entry_image_path[len(prefix):]

            image_url = f"/static/uploads/{entry_image_path}"
        else:
            image_url = None

        print("Ruta final utilizada:", image_url)  # Para depuración

        trade_list.append({
            "trade_id": trade["id"],
            "notebook_name": trade["notebook_name"],
            "asset": trade["asset"],
            "lot_size": trade["lot_size"],
            "entry_point": trade["entry_point"],
            "stop_loss": trade["stop_loss"],
            "take_profit": trade["take_profit"],
            "result": trade["result"],
            "trade_date": trade["trade_date"],
            "emotion": trade["emotion"],
            "activation_routine": "Sí" if str(trade["activation_routine"]).lower() in ["sí", "si", "yes", "1"] else "No",
            "profit_loss": profit_loss_display,
            "entry_image_url": image_url
        })

    return jsonify({"trades": trade_list})



@app.route('/eliminar_trade', methods=['POST'])
def eliminar_trade():
    try:
        print("=== DEBUG ELIMINAR TRADE ===")
        print("Request method:", request.method)
        print("Request content type:", request.content_type)
        print("Request form:", request.form)
        
        trade_id = request.form.get('trade_id')
        csrf_token = request.form.get('csrf_token')
        
        print("Trade ID recibido:", trade_id, "Tipo:", type(trade_id))
        print("CSRF token recibido:", csrf_token)
        
        if not trade_id:
            print("ERROR: ID de trade no proporcionado")
            return jsonify({"error": "ID de trade no proporcionado"}), 400
        
        # Convertir a entero si es string
        try:
            trade_id = int(trade_id)
        except (ValueError, TypeError):
            print("ERROR: Trade ID no es un número válido")
            return jsonify({"error": "ID de trade no es un número válido"}), 400
        
        print("User ID de sesión:", session.get('user_id'))
        
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Verificar que el trade existe y pertenece al usuario
        cursor.execute("SELECT id FROM trades WHERE id = ? AND user_id = ?", (trade_id, session['user_id']))
        trade = cursor.fetchone()
        print("Trade encontrado:", trade)
        
        if not trade:
            connection.close()
            print("ERROR: Trade no encontrado o sin permisos")
            return jsonify({"error": "Trade no encontrado o no tienes permisos para eliminarlo"}), 404
        
        # Eliminar el trade
        cursor.execute("DELETE FROM trades WHERE id = ? AND user_id = ?", (trade_id, session['user_id']))
        rows_affected = cursor.rowcount
        print("Filas afectadas:", rows_affected)
        
        connection.commit()
        connection.close()
        
        print("SUCCESS: Trade eliminado correctamente")
        return jsonify({"success": "El trade ha sido eliminado con éxito."})
        
    except Exception as e:
        print(f"ERROR EXCEPTION al eliminar trade: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Error interno del servidor al eliminar el trade: {str(e)}"}), 500

from flask import send_file

@app.route('/descargar_historial', methods=['GET'])
def descargar_historial():
    try:
        notebook_id = request.args.get('notebook_id')

        connection = get_db_connection()
        cursor = connection.cursor()

        # Consulta para obtener los trades según el filtro de cuaderno
        if notebook_id:
            cursor.execute("""
                SELECT t.*, n.name as notebook_name
                FROM trades t
                JOIN notebooks n ON t.notebook_id = n.id
                WHERE t.user_id = ? AND t.notebook_id = ?
                ORDER BY t.trade_date DESC
            """, (session['user_id'], notebook_id))
        else:
            cursor.execute("""
                SELECT t.*, n.name as notebook_name
                FROM trades t
                JOIN notebooks n ON t.notebook_id = n.id
                WHERE t.user_id = ?
                ORDER BY t.trade_date DESC
            """, (session['user_id'],))

        trades = cursor.fetchall()
        connection.close()

        # Verificar si se obtuvieron resultados
        if not trades:
            return jsonify({"error": "No hay datos disponibles para descargar."}), 404

        # Definir los nombres de las columnas en el orden correcto
        columnas = [
            'Cuaderno', 'Activo Operado', 'Lotaje Operado', 'Punto de Entrada',
            'Stop Loss', 'Take Profit', 'Resultado de la Operación',
            'Fecha de la Operación', 'Emoción al Operar',
            '¿Realizaste la rutina de activación?', 'Ganancia / Pérdida', 'Imagen de Entrada'
        ]

        trade_list = []
        for trade in trades:
            # Calcular ganancia/pérdida
            if trade['result'] == 'Ganadora':
                profit_loss = abs((trade['take_profit'] - trade['entry_point']) * trade['lot_size']) if 'Boom' in trade['asset'] else abs((trade['entry_point'] - trade['take_profit']) * trade['lot_size'])
            elif trade['result'] == 'Perdedora':
                profit_loss = abs((trade['entry_point'] - trade['stop_loss']) * trade['lot_size']) if 'Boom' in trade['asset'] else abs((trade['stop_loss'] - trade['entry_point']) * trade['lot_size'])
            else:
                profit_loss = 0

            profit_loss_display = f"{profit_loss} USD"
            image_url = trade["entry_image_path"] if trade["entry_image_path"] else 'N/A'

            trade_list.append([
                trade["notebook_name"], trade["asset"], trade["lot_size"],
                trade["entry_point"], trade["stop_loss"], trade["take_profit"],
                trade["result"], trade["trade_date"], trade["emotion"],
                "Sí" if str(trade["activation_routine"]).lower() in ["sí", "si", "yes", "1"] else "No",
                profit_loss_display, image_url
            ])

        df = pd.DataFrame(trade_list, columns=columnas)
        df = df.astype(str)

        print("Estructura del DataFrame antes de exportar a Excel:")
        print(df.head())

        if df.empty:
            print("El DataFrame está vacío después de crear desde la consulta.")
            return jsonify({"error": "El DataFrame está vacío."}), 500

        uploads_dir = os.path.join(app.root_path, 'static/uploads')
        if not os.path.exists(uploads_dir):
            os.makedirs(uploads_dir)
        excel_path = os.path.join(uploads_dir, 'historial_trades.xlsx')

        # Utilizar xlsxwriter como engine para evitar problemas con np.float
        df.to_excel(excel_path, index=False, engine='xlsxwriter')

        return send_file(excel_path, as_attachment=True, download_name='historial_trades.xlsx')

    except Exception as e:
        print(f"Error al descargar el historial: {str(e)}")
        return jsonify({"error": "Hubo un error al descargar el historial."}), 500

@app.route('/eliminar_cuaderno', methods=['POST'])
def eliminar_cuaderno():
    notebook_id = request.form.get('notebook_id')

    if not notebook_id:
        return jsonify({"error": "No se proporcionó un cuaderno para eliminar."}), 400

    connection = get_db_connection()
    cursor = connection.cursor()

    # Eliminar todos los registros relacionados con el cuaderno
    cursor.execute("DELETE FROM trades WHERE notebook_id = ?", (notebook_id,))
    cursor.execute("DELETE FROM notebooks WHERE id = ?", (notebook_id,))

    connection.commit()
    connection.close()

    return jsonify({"success": "Cuaderno eliminado correctamente."})

import json
import websocket
import pandas as pd
import matplotlib.pyplot as plt
import mplfinance as mpf
from flask import Flask, render_template, request, jsonify, send_file, session
from scipy.signal import find_peaks
import threading
import os
import uuid
from datetime import datetime, timedelta

# Configurar backend de matplotlib para evitar problemas con tkinter
plt.switch_backend('Agg')

# Production-ready secret key handling
app.secret_key = os.getenv('SECRET_KEY', 'clave_super_secreta')

indices_sinteticos = {
    "1": "BOOM1000",
    "2": "BOOM500",
    "3": "BOOM300N",
    "4": "CRASH1000",
    "5": "CRASH500",
    "6": "CRASH300N",
}

# Ruta para el módulo de scripts
@app.route('/scripts')
def scripts():
    # Borrar la imagen previa si existe
    if 'grafico' in session:
        try:
            os.remove(session['grafico'])
        except FileNotFoundError:
            pass
        session.pop('grafico', None)

    return render_template('scripts.html', indices_sinteticos=indices_sinteticos)

# Ruta para ejecutar el script de análisis
@app.route('/ejecutar_script', methods=['POST'])
def ejecutar_script():
    try:
        data = request.get_json()
        indice_seleccionado = data.get("indice")
        api_token = data.get("api_token")

        if not indice_seleccionado or not api_token:
            return jsonify({"error": "No se seleccionó un índice o no se proporcionó el token de API."}), 400

        # Generar un nombre de archivo único para el gráfico
        img_filename = f"static/img/grafico_{uuid.uuid4().hex}.png"
        session['grafico'] = img_filename

        # Ejecutar la conexión en un hilo separado para evitar que se bloquee la respuesta
        thread = threading.Thread(target=conectar_y_analizar_indice, args=(api_token, indice_seleccionado, img_filename))
        thread.start()

        return jsonify({"success": "Análisis en proceso. Puedes ver el gráfico cuando esté listo."})
    except Exception as e:
        print(f"Error en /ejecutar_script: {str(e)}")
        return jsonify({"error": "Hubo un error al ejecutar el script. Verifica los datos ingresados y vuelve a intentarlo."}), 500

def conectar_y_analizar_indice(api_token, indice_sintetico, img_filename):
    try:
        ws = websocket.WebSocketApp("wss://ws.binaryws.com/websockets/v3?app_id=64422",
                                    on_open=lambda ws: on_open_wrapper(ws, api_token, indice_sintetico),
                                    on_message=lambda ws, message: on_message(ws, message, img_filename, indice_sintetico),
                                    on_error=on_error,
                                    on_close=on_close)
        ws.run_forever(ping_interval=30, ping_timeout=10)
    except Exception as e:
        print(f"Error al conectar y analizar índice: {str(e)}")

def on_open_wrapper(ws, api_token, indice_sintetico):
    try:
        # Autenticación con el API token
        auth_request = {
            "authorize": api_token
        }
        ws.send(json.dumps(auth_request))
    except Exception as e:
        print(f"Error en on_open_wrapper: {str(e)}")

def on_message(ws, message, img_filename, indice_sintetico):
    try:
        data = json.loads(message)
        if 'error' in data:
            print(f"Error en la API: {data['error']['message']}")
        elif 'authorize' in data:
            print(f"Autenticación exitosa para el usuario {data['authorize']['loginid']}")
            # Después de la autenticación exitosa, enviar la solicitud de datos del índice
            obtener_datos_indice_sintetico(ws, indice_sintetico)
        elif 'candles' in data:
            analizar_indice(data['candles'], img_filename)
        else:
            print("Respuesta inesperada de la API:", json.dumps(data, indent=4))
    except Exception as e:
        print(f"Error en on_message: {str(e)}")

def on_error(ws, error):
    print(f"Error en la conexión: {error}")

def on_close(ws, close_status_code, close_msg):
    print(f"Conexión WebSocket cerrada con código: {close_status_code} y mensaje: {close_msg}")

def obtener_datos_indice_sintetico(ws, symbol):
    try:
        # Obtener la fecha de hace 12 horas
        fecha_12_horas_atras = int((datetime.now() - timedelta(hours=12)).timestamp())

        request_data = {
            "ticks_history": symbol,
            "adjust_start_time": 1,
            "count": 500,  # Más datos para mejorar la detección de máximos y mínimos
            "end": "latest",
            "start": fecha_12_horas_atras,
            "style": "candles",
            "granularity": 1800  # Granularidad de 30 minutos
        }
        print(f"Enviando solicitud para el índice: {symbol}")
        ws.send(json.dumps(request_data))
    except Exception as e:
        print(f"Error en obtener_datos_indice_sintetico: {str(e)}")

def analizar_indice(candles, img_filename):
    try:
        # Convertir los datos a un formato que pueda ser utilizado por mplfinance
        ohlc_data = {
            'Date': [pd.to_datetime(candle['epoch'], unit='s') for candle in candles],
            'Open': [candle['open'] for candle in candles],
            'High': [candle['high'] for candle in candles],
            'Low': [candle['low'] for candle in candles],
            'Close': [candle['close'] for candle in candles]
        }
        df = pd.DataFrame(ohlc_data)
        df.set_index('Date', inplace=True)

        # Detectar máximos y mínimos que no han sido cortados
        high_prices = df['High']
        low_prices = df['Low']
        close_prices = df['Close']

        # Detectar los picos máximos y mínimos
        max_peaks, _ = find_peaks(high_prices, distance=3)
        min_peaks, _ = find_peaks(-low_prices, distance=3)

        # Filtrar los máximos y mínimos que no han sido rotos por el precio de cierre
        max_not_broken = [peak for peak in max_peaks if high_prices.iloc[peak] > max(close_prices.iloc[peak:])]
        min_not_broken = [valley for valley in min_peaks if low_prices.iloc[valley] < min(close_prices.iloc[valley:])]

        # Crear el gráfico de velas japonesas con mplfinance
        mc = mpf.make_marketcolors(up='g', down='r', wick='i', edge='i')
        s = mpf.make_mpf_style(marketcolors=mc, gridstyle='--', y_on_right=False)

        fig, axlist = mpf.plot(df, type='candle', style=s, returnfig=True, figsize=(14, 8))

        # Añadir líneas horizontales para máximos y mínimos no cortados
        ax = axlist[0]  # Obtener el eje principal de la gráfica
        for peak in max_not_broken:
            ax.axhline(y=high_prices.iloc[peak], color='blue', linestyle='--', linewidth=1, alpha=0.6, label='Máximo sin cortar' if peak == max_not_broken[0] else "")

        for valley in min_not_broken:
            ax.axhline(y=low_prices.iloc[valley], color='purple', linestyle='--', linewidth=1, alpha=0.6, label='Mínimo sin cortar' if valley == min_not_broken[0] else "")

        # Configurar leyenda para mostrar solo una vez
        handles, labels = ax.get_legend_handles_labels()
        by_label = dict(zip(labels, handles))
        ax.legend(by_label.values(), by_label.keys())

        # Guardar la imagen
        plt.savefig(img_filename, format='png', bbox_inches='tight', dpi=200)
        plt.close()
    except Exception as e:
        print(f"Error en analizar_indice: {str(e)}")

@app.route('/mostrar_grafico')
def mostrar_grafico():
    # Devolver la imagen generada al frontend
    if 'grafico' in session and os.path.exists(session['grafico']):
        return send_file(session['grafico'], mimetype='image/png')
    else:
        return "Gráfico no disponible.", 404


# Rutas para el gráfico en vivo
@app.route('/inicio')
def inicio():
    return render_template('inicio.html', indices_sinteticos=indices_sinteticos)

@app.route('/datos_grafico')
def datos_grafico():
    indice = request.args.get('indice')
    temporalidad = request.args.get('temporalidad', type=int)

    if not indice or not temporalidad:
        return jsonify({"error": "No se proporcionó un índice o temporalidad."}), 400

    try:
        # Obtener datos del índice desde la API según la temporalidad
        datos = obtener_datos_indice_vivo(indice, temporalidad)
        if datos is None or datos.empty:
            return jsonify({"error": "Error al obtener datos del índice."}), 500

        # Convertir DataFrame a listas para el frontend
        tiempos = datos['time'].dt.strftime('%Y-%m-%d %H:%M:%S').tolist()
        open_prices = datos['open'].tolist()
        high_prices = datos['high'].tolist()
        low_prices = datos['low'].tolist()
        close_prices = datos['close'].tolist()

        return jsonify({"tiempos": tiempos, "open": open_prices, "high": high_prices, "low": low_prices, "close": close_prices})
    except Exception as e:
        import traceback
        print(f"Error en /datos_grafico: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({"error": f"Hubo un error al obtener los datos del gráfico: {str(e)}"}), 500

def obtener_datos_indice_vivo_local(symbol, granularity):
    # Generar datos mock para testing
    import random
    base_price = 1000
    candles = []
    current_time = int(datetime.now().timestamp())
    for i in range(1000):
        epoch = current_time - (1000 - i) * granularity * 60
        open_price = base_price + random.uniform(-10, 10)
        high_price = open_price + random.uniform(0, 5)
        low_price = open_price - random.uniform(0, 5)
        close_price = open_price + random.uniform(-5, 5)
        candles.append({
            "epoch": epoch,
            "open": round(open_price, 2),
            "high": round(high_price, 2),
            "low": round(low_price, 2),
            "close": round(close_price, 2)
        })
        base_price = close_price
    return candles

# Módulo de Gestión de Riesgo

from flask import Flask, render_template, request, jsonify, session
import pandas as pd

import sqlite3


# Production-ready secret key handling
app.secret_key = os.getenv('SECRET_KEY', 'clave_super_secreta')

def get_db_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection

# Ruta para mostrar el módulo de Gestión de Riesgo
@app.route('/gestion_riesgo')
def gestion_riesgo():
    return render_template('gestion_riesgo.html')

# Cálculo de lotaje basado en riesgo fijo
@app.route('/calcular_lotaje', methods=['POST'])
def calcular_lotaje():
    try:
        # Datos de entrada
        balance = request.form.get('balance', type=float)
        riesgo_por_trade = request.form.get('riesgo_por_trade', type=float)  # Riesgo en porcentaje
        stop_loss_pips = request.form.get('stop_loss_pips', type=float)
        valor_por_pip = request.form.get('valor_por_pip', type=float)

        # Cálculo del riesgo en USD
        riesgo_usd = (balance * (riesgo_por_trade / 100))

        # Cálculo del lotaje
        lotaje = riesgo_usd / (stop_loss_pips * valor_por_pip)

        return jsonify({"lotaje": round(lotaje, 2)})
    except Exception as e:
        print(f"Error al calcular lotaje: {str(e)}")
        return jsonify({"error": "Hubo un error al calcular el lotaje."}), 500

# Cálculo del nivel de exposición total y diversificación
@app.route('/nivel_exposicion', methods=['GET'])
def nivel_exposicion():
    try:
        user_id = session['user_id']
        connection = get_db_connection()
        cursor = connection.cursor()

        # Obtener todas las operaciones abiertas del usuario
        cursor.execute("SELECT asset, lot_size, entry_point FROM trades WHERE user_id = ? AND status = 'Abierta'", (user_id,))
        trades = cursor.fetchall()
        connection.close()

        # Calcular la exposición total por activo
        exposicion_por_activo = {}
        for trade in trades:
            asset = trade['asset']
            lot_size = trade['lot_size']
            exposicion_por_activo[asset] = exposicion_por_activo.get(asset, 0) + lot_size

        exposicion_total = sum(exposicion_por_activo.values())

        return jsonify({"exposicion_por_activo": exposicion_por_activo, "exposicion_total": exposicion_total})
    except Exception as e:
        print(f"Error al calcular el nivel de exposición: {str(e)}")
        return jsonify({"error": "Hubo un error al calcular el nivel de exposición."}), 500

# Análisis de Drawdown
@app.route('/analisis_drawdown', methods=['GET'])
def analisis_drawdown():
    try:
        user_id = session['user_id']
        connection = get_db_connection()
        cursor = connection.cursor()

        # Obtener el historial de capital de la cuenta del usuario
        cursor.execute("SELECT trade_date, capital FROM capital_history WHERE user_id = ? ORDER BY trade_date", (user_id,))
        capital_data = cursor.fetchall()
        connection.close()

        if not capital_data:
            return jsonify({"error": "No hay datos de capital disponibles."}), 404

        # Convertir los datos en un DataFrame para realizar el análisis
        df = pd.DataFrame(capital_data, columns=['trade_date', 'capital'])
        df['trade_date'] = pd.to_datetime(df['trade_date'])
        df.set_index('trade_date', inplace=True)

        # Cálculo del drawdown
        capital_max = df['capital'].cummax()
        drawdown = (capital_max - df['capital']) / capital_max
        drawdown_actual = drawdown.iloc[-1]
        drawdown_maximo = drawdown.max()

        # Convertir datos para la visualización del gráfico
        fechas = df.index.strftime('%Y-%m-%d %H:%M:%S').tolist()
        balances = df['capital'].tolist()
        drawdowns = (drawdown * 100).tolist()

        return jsonify({
            "drawdown_actual": round(drawdown_actual * 100, 2),
            "drawdown_maximo": round(drawdown_maximo * 100, 2),
            "fechas": fechas,
            "balances": balances,
            "drawdowns": drawdowns
        })
    except Exception as e:
        print(f"Error al realizar el análisis de drawdown: {str(e)}")
        return jsonify({"error": "Hubo un error al realizar el análisis de drawdown."}), 500

from flask import Flask, render_template, jsonify, request, session
import pandas as pd
import os
import sqlite3

# Production-ready secret key handling
app.secret_key = os.getenv('SECRET_KEY', 'secret_key')

@app.route('/gamificacion', methods=['GET', 'POST'])
def gamificacion():
    try:
        user_id = session['user_id']
        connection = get_db_connection()
        cursor = connection.cursor()

        if request.method == 'POST':
            selected_month = request.form['selected_month']
            
            # Obtener el historial de trades para el mes seleccionado
            cursor.execute("""
                SELECT result, lot_size, entry_point, take_profit, stop_loss, trade_date, emotion
                FROM trades 
                WHERE user_id = ? AND strftime('%Y-%m', trade_date) = ?
                ORDER BY trade_date
            """, (user_id, selected_month))
            trades = cursor.fetchall()

            if not trades:
                connection.close()
                return render_template('gamificacion.html', 
                                     months=[selected_month], 
                                     selected_month=selected_month,
                                     error_message="No hay datos disponibles para el mes seleccionado.")

            # Crear estructura de gamificación
            metas = [
                {"id": 1, "descripcion": "Conseguir 3 operaciones ganadoras consecutivas", "cumplida": False, "progreso": 0},
                {"id": 2, "descripcion": "Lograr un 20% de rentabilidad en un mes", "cumplida": False, "progreso": 0},
                {"id": 3, "descripcion": "Gestionar mejor mis emociones al operar", "cumplida": False, "progreso": 0},
                {"id": 4, "descripcion": "Registrar cada trade correctamente por 1 mes", "cumplida": False, "progreso": 0},
                {"id": 5, "descripcion": "Mantener un drawdown inferior al 5% durante un mes", "cumplida": False, "progreso": 0}
            ]

            # Variables auxiliares para calcular el progreso de las metas
            consecutivas_ganadoras = 0
            total_trades = len(trades)
            ganancia_total = 0
            drawdown_maximo = 0
            emociones_positivas = ["Confianza", "Tranquilidad"]
            emociones_positivas_count = 0

            # Análisis de los trades
            for trade in trades:
                # Meta 1: Conseguir 3 operaciones ganadoras consecutivas
                if trade['result'] == 'Ganadora':
                    consecutivas_ganadoras += 1
                else:
                    consecutivas_ganadoras = 0

                if consecutivas_ganadoras >= 3:
                    metas[0]['cumplida'] = True
                    metas[0]['progreso'] = 100
                else:
                    metas[0]['progreso'] = min((consecutivas_ganadoras / 3) * 100, 100)

                # Meta 2: Lograr un 20% de rentabilidad en un mes (simple aproximación)
                if trade['result'] == 'Ganadora':
                    ganancia_total += abs(trade['take_profit'] - trade['entry_point']) * trade['lot_size']
                elif trade['result'] == 'Perdedora':
                    ganancia_total -= abs(trade['entry_point'] - trade['stop_loss']) * trade['lot_size']

                # Meta 3: Gestionar mejor mis emociones (contar emociones positivas)
                if trade['emotion'] in emociones_positivas:
                    emociones_positivas_count += 1

            # Rentabilidad del 20%
            rentabilidad_porcentaje = (ganancia_total / (trades[0]['entry_point'] * trades[0]['lot_size'])) * 100
            metas[1]['progreso'] = min(max((rentabilidad_porcentaje / 20) * 100, 0), 100)
            if rentabilidad_porcentaje >= 20:
                metas[1]['cumplida'] = True

            # Emociones positivas durante el mes
            metas[2]['progreso'] = min((emociones_positivas_count / total_trades) * 100, 100)
            if metas[2]['progreso'] >= 80:
                metas[2]['cumplida'] = True

            # Meta 4: Registrar cada trade correctamente por 1 mes
            metas[3]['progreso'] = min((total_trades / 30) * 100, 100)
            if total_trades >= 30:
                metas[3]['cumplida'] = True

            # Meta 5: Mantener un drawdown inferior al 5% durante un mes (simplificado)
            drawdown_maximo = max(0.05 - (ganancia_total / total_trades), 0)
            metas[4]['progreso'] = min((1 - drawdown_maximo) * 100, 100)
            if drawdown_maximo <= 0.05:
                metas[4]['cumplida'] = True

            return render_template('gamificacion.html', metas=metas, selected_month=selected_month)

        else:
            # Obtener los meses disponibles en los que se han realizado operaciones
            cursor.execute("""
                SELECT DISTINCT strftime('%Y-%m', trade_date) as month
                FROM trades
                WHERE user_id = ?
                ORDER BY month DESC
            """, (user_id,))
            months = [row['month'] for row in cursor.fetchall()]

            connection.close()

            return render_template('gamificacion.html', months=months)

    except Exception as e:
        print(f"Error en el módulo de gamificación: {str(e)}")
        return render_template('gamificacion.html', 
                             months=[], 
                             error_message="Hubo un error al procesar la solicitud. Intenta nuevamente.")



from flask import Flask, render_template, jsonify, request, send_file
from strategies.combined import check_combined_strategies
from utils.indicator_calculator import calcular_indicadores
from models.random_forest import entrenar_modelo_rf
from strategies.scalping_hybrid import estrategia_scalping_hybrid
import os

indices_sinteticos = {
    "1": "BOOM1000",
    "2": "BOOM500",
    "3": "BOOM300N",
    "4": "CRASH1000",
    "5": "CRASH500",
    "6": "CRASH300N",
}

temporalidades = [
    {"value": 1, "label": "1 minuto"},
    {"value": 5, "label": "5 minutos"},
    {"value": 15, "label": "15 minutos"},
    {"value": 30, "label": "30 minutos"},
]

@app.route('/estrategias', methods=['GET'])
def estrategias():
    return render_template('estrategias.html', indices_sinteticos=indices_sinteticos, temporalidades=temporalidades)

@app.route('/ejecutar_estrategias', methods=['POST'])
def ejecutar_estrategias():
    try:
        activo_seleccionado = request.form.get("indice")
        temporalidad = request.form.get("temporalidad")
        if not activo_seleccionado or not temporalidad:
            return jsonify({"error": "No se seleccionó un índice o una temporalidad"}), 400

        temporalidad = int(temporalidad)
        activo = indices_sinteticos.get(activo_seleccionado)
        if not activo:
            return jsonify({"error": "Índice no válido"}), 400

        resultados = []
        resultado_combinado = check_combined_strategies(activo, temporalidad)

        if resultado_combinado:
            resultados.append(resultado_combinado)
        else:
            resultados.append({
                "strategy_name": "Estrategia Combinada",
                "asset": activo,
                "status": "No se encontró oportunidad",
                "win_rate": 10  # Probabilidad por defecto si no se encuentra oportunidad
            })

        app.config['ULTIMAS_OPORTUNIDADES'] = resultados

        return jsonify({"message": "Las estrategias se están ejecutando. Verifica los resultados en unos segundos."})

    except Exception as e:
        print(f"Error en ejecutar_estrategias: {str(e)}")
        return jsonify({"error": f"Hubo un error al ejecutar las estrategias: {str(e)}"}), 500

@app.route('/resultado_estrategias', methods=['GET'])
def resultado_estrategias():
    resultados = app.config.get('ULTIMAS_OPORTUNIDADES', [])
    return jsonify({"resultados": resultados})


from flask import Flask, request, jsonify
from strategies.scalping_hybrid import estrategia_scalping_hybrid
import datetime


# Definición del endpoint para ejecutar la estrategia
@app.route('/ejecutar_estrategia_scalping_hybrid', methods=['POST'])
def ejecutar_estrategia_scalping_hybrid():
    try:
        # Obtener los datos del formulario
        activo_seleccionado = request.form.get("indice")
        temporalidad = request.form.get("temporalidad")

        # Validar que se hayan ingresado un índice y una temporalidad
        if not activo_seleccionado or not temporalidad:
            return jsonify({"error": "Datos incompletos. Por favor ingrese todos los datos requeridos."}), 400

        temporalidad = int(temporalidad)
        activo = indices_sinteticos.get(activo_seleccionado)

        # Validar que el índice seleccionado sea válido
        if not activo:
            return jsonify({"error": "Índice no válido"}), 400

        # Ejecutar la estrategia combinada de scalping e híbrido
        resultado = estrategia_scalping_hybrid(activo, temporalidad)

        if resultado:
            # Guardar los resultados en una variable global para obtenerlos luego
            app.config['ULTIMAS_OPORTUNIDADES'] = [resultado]
        else:
            app.config['ULTIMAS_OPORTUNIDADES'] = [{
                "strategy_name": "Scalping-Hybrid",
                "asset": activo,
                "entry_point": "Valor predeterminado utilizado",
                "stop_loss": "Valor predeterminado utilizado",
                "take_profit": "Valor predeterminado utilizado",
                "win_rate": "0%",
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "message": "No se encontró oportunidad, probabilidad de éxito es del 0%"
            }]

        return jsonify({"message": "La estrategia combinada se está ejecutando. Verifica los resultados en unos segundos."})

    except Exception as e:
        print(f"Error en ejecutar_estrategia_scalping_hybrid: {str(e)}")
        return jsonify({"error": f"Hubo un error al ejecutar la estrategia: {str(e)}"}), 500


from flask import Flask, render_template, jsonify, request, redirect, url_for
import sqlite3
from config import DB_PATH

# Definición de meses y hábitos
meses = {
    "1": "Enero", "2": "Febrero", "3": "Marzo", "4": "Abril", "5": "Mayo", "6": "Junio",
    "7": "Julio", "8": "Agosto", "9": "Septiembre", "10": "Octubre", "11": "Noviembre", "12": "Diciembre"
}
habitos = [
    "Ir al GYM", "Meditar", "NDP", "Vida social", "Estado de ánimo",
    "Relación familiar", "Lectura", "Inglés", "Trabajo", "Trading"
]


@app.route('/control_habitos', methods=['GET'])
def control_habitos():
    return render_template('control_habitos.html', meses=meses, habitos=habitos)

@app.route('/habitos/<mes>', methods=['GET'])
def obtener_habitos(mes):
    try:
        user_id = 1
        connection = sqlite3.connect(DB_PATH)
        cursor = connection.cursor()

        cursor.execute('''
            SELECT habito, dia, cumplido FROM habitos WHERE user_id = ? AND mes = ?
        ''', (user_id, mes))
        registros = cursor.fetchall()

        habitos_data = {}
        for habito, dia, cumplido in registros:
            if habito not in habitos_data:
                habitos_data[habito] = []
            habitos_data[habito].append({"dia": dia, "cumplido": cumplido})

        habitos_list = [{"nombre": habito, "dias": dias} for habito, dias in habitos_data.items()]

        return jsonify({"habitos": habitos_list})
    except Exception as e:
        print(f"Error al obtener hábitos: {str(e)}")
        return jsonify({"error": "Error al obtener hábitos"}), 500
    finally:
        connection.close()

@app.route('/habitos/<mes>/actualizar', methods=['POST'])
def actualizar_habito(mes):
    try:
        print("=== DEBUG ACTUALIZAR HÁBITO ===")
        print("Request method:", request.method)
        print("Request content type:", request.content_type)
        print("Request form:", request.form)
        print("Mes:", mes)
        
        # Obtener datos del request
        if request.is_json:
            data = request.get_json()
            habito = data.get("habito")
            dia = data.get("dia")
            cumplido = data.get("cumplido", True)
            print("JSON data:", data)
        else:
            habito = request.form.get("habito")
            dia = request.form.get("dia")
            cumplido = request.form.get("cumplido", "true").lower() == "true"
            print("Form data:", request.form)
        
        print("Datos procesados:", {"habito": habito, "dia": dia, "cumplido": cumplido})
        
        if not habito or not dia:
            print("ERROR: Datos faltantes")
            return jsonify({"error": "Datos de hábito y día son requeridos"}), 400
        
        # Usar el user_id de la sesión
        user_id = session.get('user_id')
        if not user_id:
            print("ERROR: Usuario no autenticado")
            return jsonify({"error": "Usuario no autenticado"}), 401
        
        print("User ID:", user_id)
        
        connection = get_db_connection()
        cursor = connection.cursor()

        # Verificar si existe el registro
        cursor.execute('''
            SELECT id FROM habitos WHERE user_id = ? AND mes = ? AND habito = ? AND dia = ?
        ''', (user_id, mes, habito, dia))
        registro = cursor.fetchone()

        if registro:
            # Actualizar registro existente
            cursor.execute('''
                UPDATE habitos SET cumplido = ? WHERE id = ?
            ''', (cumplido, registro[0]))
            print("Registro actualizado:", registro[0])
        else:
            # Crear nuevo registro
            cursor.execute('''
                INSERT INTO habitos (user_id, mes, habito, dia, cumplido) VALUES (?, ?, ?, ?, ?)
            ''', (user_id, mes, habito, dia, cumplido))
            print("Nuevo registro creado")

        connection.commit()
        connection.close()
        
        print("SUCCESS: Hábito actualizado correctamente")
        return jsonify({"message": "Hábito actualizado correctamente"})
        
    except Exception as e:
        print(f"ERROR EXCEPTION al actualizar hábito: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Error interno del servidor: {str(e)}"}), 500

@app.route('/estadisticas_habitos/<mes>', methods=['GET'])
def estadisticas_habitos(mes):
    try:
        user_id = 1
        connection = sqlite3.connect(DB_PATH)
        cursor = connection.cursor()

        cursor.execute('''
            SELECT habito, COUNT(*) as cumplidos FROM habitos WHERE user_id = ? AND mes = ? AND cumplido = 1 GROUP BY habito
        ''', (user_id, mes))
        registros = cursor.fetchall()

        habitos_data = [{"nombre": registro[0], "cumplimiento": registro[1]} for registro in registros]

        return render_template("estadisticas_habitos.html", habitos=habitos_data, mes=meses.get(mes, ""))
    except Exception as e:
        print(f"Error al obtener estadísticas: {str(e)}")
        return jsonify({"error": "Error al obtener estadísticas"}), 500
    finally:
        connection.close()


from flask import Flask, render_template, jsonify, request, session, redirect, url_for
import sqlite3


# Ruta para manejar la vista del módulo de cuadernos
@app.route('/personal_notebooks', methods=['GET', 'POST'])
def personal_notebooks():
    try:
        # Verificar que el usuario esté autenticado
        if 'user_id' not in session:
            return jsonify({'error': 'Usuario no autenticado'}), 401
        
        user_id = session['user_id']
        print(f"DEBUG: User ID from session: {user_id}")
        
        connection = get_db_connection()
        cursor = connection.cursor()

        if request.method == 'POST':
            print(f"DEBUG: POST request received")
            print(f"DEBUG: Request form: {request.form}")
            
            # Verificar que el action esté presente
            if 'action' not in request.form:
                return jsonify({'error': 'Acción no especificada'}), 400
            
            action = request.form['action']
            print(f"DEBUG: Action: {action}")

            # Crear un cuaderno
            if action == 'create_notebook':
                if 'notebook_name' not in request.form:
                    return jsonify({'error': 'Nombre del cuaderno requerido'}), 400
                
                notebook_name = request.form['notebook_name'].strip()
                if not notebook_name:
                    return jsonify({'error': 'El nombre del cuaderno no puede estar vacío'}), 400
                
                print(f"DEBUG: Creating notebook: {notebook_name}")
                
                cursor.execute('''
                    INSERT INTO personal_notebooks (user_id, name, content)
                    VALUES (?, ?, ?)
                ''', (user_id, notebook_name, ""))
                connection.commit()
                
                notebook_id = cursor.lastrowid
                print(f"DEBUG: Notebook created with ID: {notebook_id}")
                
                return jsonify({
                    'message': 'Cuaderno creado exitosamente.',
                    'notebook_id': notebook_id,
                    'notebook_name': notebook_name
                })

            # Eliminar un cuaderno
            elif action == 'delete_notebook':
                if 'personal_notebook_id' not in request.form:
                    return jsonify({'error': 'ID del cuaderno requerido'}), 400
                
                personal_notebook_id = request.form['personal_notebook_id']
                print(f"DEBUG: Deleting notebook ID: {personal_notebook_id}")
                
                # Verificar que el cuaderno pertenece al usuario
                cursor.execute('''
                    SELECT id FROM personal_notebooks WHERE id = ? AND user_id = ?
                ''', (personal_notebook_id, user_id))
                
                if not cursor.fetchone():
                    return jsonify({'error': 'Cuaderno no encontrado o sin permisos'}), 404
                
                cursor.execute('''
                    DELETE FROM personal_notebooks WHERE id = ? AND user_id = ?
                ''', (personal_notebook_id, user_id))
                connection.commit()
                
                print(f"DEBUG: Notebook deleted successfully")
                return jsonify({'message': 'Cuaderno eliminado exitosamente.'})
            
            else:
                return jsonify({'error': 'Acción no válida'}), 400

        # Obtener todos los cuadernos del usuario
        cursor.execute('''
            SELECT * FROM personal_notebooks WHERE user_id = ?
        ''', (user_id,))
        notebooks = cursor.fetchall()
        
        print(f"DEBUG: Found {len(notebooks)} notebooks for user {user_id}")

        connection.close()
        return render_template('notebooks.html', notebooks=notebooks)

    except Exception as e:
        print(f"ERROR en el módulo de cuadernos: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Hubo un error en el módulo de cuadernos: {str(e)}'}), 500

# Conexión a la base de datos
def get_db_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection

# Ruta para trabajar en una página específica (nota)
@app.route('/edit_notebook/<int:notebook_id>', methods=['GET', 'POST'])
def edit_notebook(notebook_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        if request.method == 'POST':
            content = request.form['content']
            cursor.execute('''
                UPDATE personal_notebooks
                SET content = ?
                WHERE id = ?
            ''', (content, notebook_id))
            connection.commit()
            connection.close()
            return jsonify({'message': 'Notas guardadas exitosamente.'})

        # Obtener el cuaderno específico
        cursor.execute('''
            SELECT * FROM personal_notebooks WHERE id = ?
        ''', (notebook_id,))
        notebook = cursor.fetchone()

        if notebook is None:
            return jsonify({'error': 'Cuaderno no encontrado.'}), 404

        connection.close()
        return render_template('edit_notebook.html', notebook=notebook)

    except Exception as e:
        print(f"Error al editar el cuaderno: {str(e)}")
        return jsonify({'error': 'Hubo un error al editar el cuaderno.'}), 500

# Production-ready server configuration
if __name__ == '__main__':
    # Initialize database on startup
    init_db()
    
    # Configure for production
    port = int(os.getenv('PORT', 5000))
    debug = not bool(os.getenv('RAILWAY_ENVIRONMENT'))
    
    app.run(host='0.0.0.0', port=port, debug=debug)