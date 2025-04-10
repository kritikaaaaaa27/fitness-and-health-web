from flask import Flask, request, render_template, jsonify, redirect, send_file, url_for, flash
import requests
from dotenv import load_dotenv
import os
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import json
import uuid

from database_connection import init_db, get_db_connection

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

# Initialize database
init_db()

login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id, name, email, password):
        self.id = id
        self.name = name
        self.email = email
        self.password = password

@login_manager.user_loader
def load_user(user_id):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    if user:
        return User(*user)
    return None

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        conn.close()
        
        if user and check_password_hash(user['password'], password):
            login_user(User(*user))
            return redirect(url_for('dashboard'))
        flash('Invalid email or password', 'danger')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = generate_password_hash(request.form['password'], method='pbkdf2:sha256')

        conn = get_db_connection()
        existing_user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        if existing_user:
            flash('An account with this email already exists.', 'danger')
        else:
            conn.execute('INSERT INTO users (name, email, password) VALUES (?, ?, ?)',
                         (name, email, password))
            conn.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        conn.close()
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return render_template('index.html')

@app.route("/")
def home():
    return render_template("index.html")

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required 
def dashboard():
    return render_template('dashboard.html')

@app.route('/goals', methods=['GET', 'POST'])
@login_required
def goals():
    return render_template('goals.html')

@app.route('/video', methods=['GET', 'POST'])
@login_required
def video():
    return render_template('video.html')


if __name__ == "__main__":
    app.run(debug=True, port=5000)