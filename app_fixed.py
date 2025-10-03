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
