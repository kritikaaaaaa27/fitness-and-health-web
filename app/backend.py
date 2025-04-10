from flask import Flask, request, render_template, redirect, url_for, flash
from dotenv import load_dotenv
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import hashlib

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

def get_user_avatar(name):
    h = hashlib.md5(name.encode()).hexdigest()
    return f"https://robohash.org/{h}?set=set5"

@app.route("/")
def home():
    return render_template("index.html")

@app.route('/dashboard')
@login_required
def dashboard():
    conn = get_db_connection()
    goals = conn.execute('SELECT * FROM goals WHERE completed = 0 ORDER BY created_at DESC').fetchall()
    videos = conn.execute('SELECT * FROM videos ORDER BY id DESC LIMIT 3').fetchall()
    threads = conn.execute('SELECT * FROM forum_threads ORDER BY created_at DESC LIMIT 3').fetchall()
    conn.close()

    threads = [dict(t) for t in threads]
    for t in threads:
        t['avatar'] = get_user_avatar(t['username'])

        print(t['avatar'])

    return render_template('dashboard.html', goals=goals, videos=videos, threads=threads)

@app.route('/goals')
@login_required
def index():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM goals WHERE completed=0')
    active_goals = cur.fetchall()

    cur.execute('SELECT * FROM goals WHERE completed=1 ORDER BY target_date DESC')
    completed_goals = cur.fetchall()
    conn.close()

    return render_template('goals.html', active_goals=active_goals, completed_goals=completed_goals)

@app.route('/add', methods=['POST'])
@login_required
def add_goal():
    goal_type = request.form['goal_type']
    start_value = float(request.form['start_value'])
    target_value = float(request.form['target_value'])
    target_date = request.form['target_date']
    note = request.form.get('motivation_note', '')

    conn = get_db_connection()
    conn.execute('''
        INSERT INTO goals (type, start_value, target_value, target_date, note, current_value)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (goal_type, start_value, target_value, target_date, note, start_value))
    conn.commit()
    conn.close()

    return redirect('/goals')

@app.route('/update/<int:goal_id>', methods=['POST'])
@login_required
def update_goal(goal_id):
    current_value = float(request.form['current_value'])
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT target_value FROM goals WHERE id = ?', (goal_id,))
    target_value = cur.fetchone()['target_value']
    completed = 1 if current_value >= target_value else 0
    cur.execute('UPDATE goals SET current_value = ?, completed = ? WHERE id = ?',
                (current_value, completed, goal_id))
    conn.commit()
    conn.close()
    return redirect('/goals')

@app.route('/videos')
@login_required
def videos():
    category = request.args.get('category')
    conn = get_db_connection()
    if category:
        rows = conn.execute('SELECT * FROM videos WHERE category = ?', (category,)).fetchall()
    else:
        rows = conn.execute('SELECT * FROM videos').fetchall()
    conn.close()
    return render_template('videos.html', videos=rows, selected_category=category)

@app.route('/forum')
@login_required
def forum():
    category = request.args.get('category')
    conn = get_db_connection()
    if category:
        rows = conn.execute('SELECT * FROM forum_threads WHERE category = ? ORDER BY created_at DESC', (category,)).fetchall()
    else:
        rows = conn.execute('SELECT * FROM forum_threads ORDER BY created_at DESC').fetchall()
    conn.close()

    threads = []
    for row in rows:
        thread = dict(row)
        thread['avatar'] = get_user_avatar(thread['username'])
        threads.append(thread)

    return render_template('forum.html', threads=threads, selected_category=category)

@app.route('/forum/new', methods=['POST'])
@login_required
def post_message():
    title = request.form['title']
    category = request.form['category']
    message = request.form['message']

    conn = get_db_connection()
    user = conn.execute('SELECT name FROM users LIMIT 1').fetchone()
    username = user['name'] if user else 'Guest'

    conn.execute('INSERT INTO forum_threads (title, username, category, message) VALUES (?, ?, ?, ?)',
                 (title, username, category, message))
    conn.commit()
    conn.close()

    return redirect('/forum')

if __name__ == "__main__":
    app.run(debug=True, port=5000)