import sqlite3
import os

def get_db_path():
    return os.path.join(os.path.dirname(__file__), 'weather.db')

def init_db():
    db_path = get_db_path()
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS searches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                city TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()

def log_search(user_id, city):
    db_path = get_db_path()
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO searches (user_id, city) VALUES (?, ?)
        ''', (user_id, city))
        conn.commit()

def get_search_history(user_id, limit=5):
    db_path = get_db_path()
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT city, COUNT(*) as count 
            FROM searches 
            WHERE user_id = ? 
            GROUP BY city 
            ORDER BY MAX(timestamp) DESC 
            LIMIT ?
        ''', (user_id, limit))
        return cursor.fetchall()

def get_search_stats():
    db_path = get_db_path()
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT city, COUNT(*) as count 
            FROM searches 
            GROUP BY city 
            ORDER BY count DESC
        ''')
        return cursor.fetchall()