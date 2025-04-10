import sqlite3
import os

def get_db_connection():
    db_file = os.path.join(os.path.dirname(__file__), 'instance', 'db.sqlite3')
    os.makedirs(os.path.dirname(db_file), exist_ok=True)
    conn = sqlite3.connect(db_file, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn

def init_db():
    conn = get_db_connection()
    with conn:
        conn.executescript('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            );
        ''')

        conn.execute('''
        CREATE TABLE IF NOT EXISTS goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            start_value REAL NOT NULL,
            target_value REAL NOT NULL,
            current_value REAL DEFAULT 0,
            target_date TEXT,
            note TEXT,
            completed INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        conn.executescript('''
            CREATE TABLE IF NOT EXISTS videos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                category TEXT NOT NULL,
                youtube_id TEXT NOT NULL
            );
        ''')

        if conn.execute('SELECT COUNT(*) FROM videos').fetchone()[0] == 0:
            conn.executemany('''
                INSERT INTO videos (title, description, category, youtube_id)
                VALUES (?, ?, ?, ?)
            ''', [
                ("Full-Body Workout", "A comprehensive full-body workout to get you in shape.", "Workouts", "dQw4w9WgXcQ"),
                ("Healthy Eating Tips", "Learn how to eat healthy and stay fit.", "Nutrition", "2Vv-BfVoq4g"),
                ("Mindfulness Meditation", "A guided meditation session for mindfulness.", "Mental Health", "3JZ_D3ELwOQ"),
                ("Productivity Hacks", "Tips to boost your productivity and stay motivated.", "Lifestyle & Motivation", "5qap5aO4i9A")
            ])

        conn.executescript('''
                CREATE TABLE IF NOT EXISTS forum_threads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                username TEXT NOT NULL,
                category TEXT NOT NULL,
                message TEXT NOT NULL,
                replies INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
        ''')

        if conn.execute('SELECT COUNT(*) FROM forum_threads').fetchone()[0] == 0:
            conn.executemany('''
                INSERT INTO forum_threads (title, username, category, message, replies) VALUES (?, ?, ?, ?, ?)
            ''', [
                ("How to start a keto diet?", "John Doe", "Nutrition", "I've been hearing a lot about the keto diet and I'm interested in starting it. Can anyone provide some tips on how to get started?", 5),
                ("Best exercises for building muscle?", "Jane Smith", "Workouts", "I'm looking to build muscle and would like to know what exercises are most effective. Any recommendations?", 8),
                ("Healthy meal prep ideas?", "Mike Johnson", "Nutrition", "I'm trying to eat healthier and would like some meal prep ideas that are both nutritious and easy to make.", 3),
                ("Managing stress through exercise?", "Sarah Lee", "Mental Health", "I've been feeling very stressed lately and heard that exercise can help. What types of exercise are best for stress relief?", 6),
                ("Supplements for joint health?", "Emily Davis", "Supplements", "I'm experiencing joint pain and am considering taking supplements. What are the best supplements for joint health?", 4),
            ])

    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")