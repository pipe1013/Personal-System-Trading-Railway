import sqlite3
from config import DB_PATH

connection = sqlite3.connect(DB_PATH)
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
print("Tablas creadas exitosamente.")
