import sqlite3
import os
import json

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

    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")