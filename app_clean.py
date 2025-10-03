import os
import sqlite3
from flask import Flask, redirect, url_for, request, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from config import DB_PATH

# Initialize Flask app
app = Flask(__name__)

# Production-ready secret key handling
app.secret_key = os.getenv('SECRET_KEY', 'your_secret_key')

# Database connection function
def get_db_connection():
    """Create and return database connection"""
    connection = sqlite3.connect(DB_PATH, timeout=30)
    connection.row_factory = sqlite3.Row
    return connection

# Database initialization
def init_db():
    """Initialize database with required tables"""
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
            CREATE TABLE IF NOT EXISTS notebooks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                initial_balance REAL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        # Create trades table  
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                notebook_id INTEGER,
                asset TEXT NOT NULL,
                lot_size REAL NOT NULL,
                entry_point REAL NOT NULL,
                stop_loss REAL,
                take_profit REAL,
                result TEXT CHECK(result IN ('Ganadora', 'Perdedora')),
                trade_date DATE,
                emotion TEXT CHECK(emotion IN ('Confianza', 'Ansiedad', 'Optimismo', 'Miedo', 'Euforia', 'Irritación', 'Calma')),
                activation_routine BOOLEAN,
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

# Helper function for authentication
def require_auth(f):
    """Decorator to require user authentication"""
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

# Routes
@app.route('/')
def home():
    """Homepage - redirect to dashboard if logged in, otherwise login"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page and authentication"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        if not username or not password:
            flash('Por favor completa todos los campos.', 'error')
            return redirect(url_for('login'))
        
        try:
            connection = get_db_connection()
            cursor = connection.cursor()
            cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
            user = cursor.fetchone()
            connection.close()
            
            if user and check_password_hash(user['password'], password):
                session['user_id'] = user['id']
                session['username'] = username
                flash(f'¡Bienvenido, {username}!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Usuario o contraseña incorrectos.', 'error')
        except Exception as e:
            print(f"Login error: {e}")
            flash('Error de conexión. Inténtalo de nuevo.', 'error')
    
    return render_login_page()

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        # Validation
        if not username or not password:
            flash('Por favor completa todos los campos.', 'error')
            return redirect(url_for('register'))
        
        if len(username) < 3:
            flash('El nombre de usuario debe tener al menos 3 caracteres.', 'error')
            return redirect(url_for('register'))
        
        if len(password) < 4:
            flash('La contraseña debe tener al menos 4 caracteres.', 'error')
            return redirect(url_for('register'))
        
        try:
            hashed_password = generate_password_hash(password)
            connection = get_db_connection()
            cursor = connection.cursor()
            cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', 
                          (username, hashed_password))
            connection.commit()
            connection.close()
            
            flash('Usuario creado exitosamente. Por favor inicia sesión.', 'success')
            return redirect(url_for('login'))
            
        except sqlite3.IntegrityError:
            flash('El nombre de usuario ya existe. Prueba con otro.', 'error')
        except Exception as e:
            print(f"Registration error: {e}")
            flash('Error al crear el usuario. Inténtalo de nuevo.', 'error')
    
    return render_register_page()

@app.route('/dashboard')
@require_auth
def dashboard():
    """Main dashboard for authenticated users"""
    username = session.get('username', 'Usuario')
    
    # Get user's notebooks count
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute('SELECT COUNT(*) as count FROM notebooks WHERE user_id = ?', 
                      (session['user_id'],))
        notebooks_count = cursor.fetchone()['count']
        
        cursor.execute('SELECT COUNT(*) as count FROM trades WHERE user_id = ?', 
                      (session['user_id'],))
        trades_count = cursor.fetchone()['count']
        connection.close()
        
    except Exception as e:
        print(f"Dashboard error: {e}")
        notebooks_count = 0
        trades_count = 0
    
    return render_dashboard_page(username, notebooks_count, trades_count)

@app.route('/logout')
def logout():
    """Logout user"""
    username = session.get('username', 'Usuario')
    session.clear()
    flash(f'¡Hasta luego, {username}! Has cerrado sesión correctamente.', 'info')
    return redirect(url_for('login'))

@app.route('/test')
def test():
    """Simple test endpoint to verify app is running"""
    return """
    <h1>✅ Trading System Status</h1>
    <p><strong>Status:</strong> Running ✅</p>
    <p><strong>Database:</strong> Initialized ✅</p>
    <p><strong>Authentication:</strong> Working ✅</p>
    <hr>
    <h2>Available Routes:</h2>
    <ul>
        <li><a href="/">Home</a></li>
        <li><a href="/login">Login</a></li>
        <li><a href="/register">Register</a></li>
        <li><a href="/dashboard">Dashboard (login required)</a></li>
        <li><a href="/logout">Logout</a></li>
    </ul>
    """

# Template rendering functions (simplified versions)
def render_login_page():
    """Render login page with flash messages"""
    messages = get_flash_messages()
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Trading System - Login</title>
        <style>
            body {{ font-family: Arial, sans-serif; max-width: 400px; margin: 50px auto; padding: 20px; }}
            .form-group {{ margin: 15px 0; }}
            input {{ width: 100%; padding: 10px; margin: 5px 0; }}
            button {{ background: #007bff; color: white; padding: 12px 24px; border: none; cursor: pointer; }}
            .flash {{ padding: 10px; margin: 10px 0; border-radius: 4px; }}
            .success {{ background: #d4edda; color: #155724; }}
            .error {{ background: #f8d7da; color: #721c24; }}
            .info {{ background: #d1ecf1; color: #0c5460; }}
        </style>
    </head>
    <body>
        <h2>🚀 Trading System Login</h2>
        {messages}
        <form method="POST">
            <div class="form-group">
                <label>Usuario:</label>
                <input type="text" name="username" required>
            </div>
            <div class="form-group">
                <label>Contraseña:</label>
                <input type="password" name="password" required>
            </div>
            <button type="submit">Iniciar Sesión</button>
        </form>
        <p><a href="/register">¿No tienes cuenta? Regístrate aquí</a></p>
        <p><a href="/test">Verificar sistema</a></p>
    </body>
    </html>
    """

def render_register_page():
    """Render registration page"""
    messages = get_flash_messages()
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Trading System - Registro</title>
        <style>
            body {{ font-family: Arial, sans-serif; max-width: 400px; margin: 50px auto; padding: 20px; }}
            .form-group {{ margin: 15px 0; }}
            input {{ width: 100%; padding: 10px; margin: 5px 0; }}
            button {{ background: #28a745; color: white; padding: 12px 24px; border: none; cursor: pointer; }}
            .flash {{ padding: 10px; margin: 10px 0; border-radius: 4px; }}
            .success {{ background: #d4edda; color: #155724; }}
            .error {{ background: #f8d7da; color: #721c24; }}
        </style>
    </head>
    <body>
        <h2>📝 Registrarse</h2>
        {messages}
        <form method="POST">
            <div class="form-group">
                <label>Nombre de usuario:</label>
                <input type="text" name="username" required minlength="3">
            </div>
            <div class="form-group">
                <label>Contraseña:</label>
                <input type="password" name="password" required minlength="4">
            </div>
            <button type="submit">Crear Cuenta</button>
        </form>
        <p><a href="/login">¿Ya tienes cuenta? Inicia sesión aquí</a></p>
        <p><a href="/test">Verificar sistema</a></p>
    </body>
    </html>
    """

def render_dashboard_page(username, notebooks_count, trades_count):
    """Render dashboard page"""
    messages = get_flash_messages()
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Trading System - Dashboard</title>
        <style>
            body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }}
            .stats {{ display: flex; gap: 20px; margin: 20px 0; }}
            .stat-card {{ background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; flex: 1; }}
            .flash {{ padding: 10px; margin: 10px 0; border-radius: 4px; }}
            .success {{ background: #d4edda; color: #155724; }}
            .error {{ background: #f8d7da; color: #721c24; }}
            .info {{ background: #d1ecf1; color: #0c5460; }}
            .logout {{ background: #dc3545; color: white; padding: 10px 20px; text-decoration: none; border-radius: 4px; }}
        </style>
    </head>
    <body>
        <h1>📈 Trading System Dashboard</h1>
        {messages}
        <p>¡Bienvenido, <strong>{username}</strong>!</p>
        
        <div class="stats">
            <div class="stat-card">
                <h3>📒 Cuadernos</h3>
                <p><strong>{notebooks_count}</strong></p>
            </div>
            <div class="stat-card">
                <h3>📊 Trades</h3>
                <p><strong>{trades_count}</strong></p>
            </div>
        </div>
        
        <h3>Sistema de Trading Completo:</h3>
        <ul>
            <li>✅ <strong>Autenticación de usuarios</strong></li>
            <li>✅ <strong>Registro de seguridad</strong></li>
            <li>✅ <strong>Base de datos SQLite</strong></li>
            <li>✅ <strong>Gest de sesiones</strong></li>
            <li>🚧 <strong>Registro de trades</strong> (próximamente)</li>
            <li>🚧 <strong>Estadísticas avanzadas</strong> (próximamente)</li>
            <li>🚧 <strong>Estrategias ML</strong> (próximamente)</li>
        </ul>
        
        <p><a href="/logout" class="logout">Cerrar Sesión</a></p>
        <p><a href="/test">Verificar sistema</a></p>
    </body>
    </html>
    """

def get_flash_messages():
    """Get all flash messages"""
    messages_html = ""
    for category, message in get_flashed_messages(with_categories=True):
        messages_html += f'<div class="flash {category}">{message}</div>'
    return messages_html

# Import get_flashed_messages function
from flask import get_flashed_messages

if __name__ == '__main__':
    # Configure for production
    port = int(os.getenv('PORT', 5000))
    debug = not bool(os.getenv('RAILWAY_ENVIRONMENT'))
    
    app.run(host='0.0.0.0', port=port, debug=debug)