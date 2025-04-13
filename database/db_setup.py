import sqlite3 
import os
from datetime import datetime

DB_PATH = "database/user_data.db"

#DB_PATH = os.path.join(os.path.dirname(__file__), 'user_data.db')

def init_db():
    """Creates the database tables if they don't exist."""
    try:
        conn = sqlite3.connect('user_data.db')
        cursor = conn.cursor()
        
        # Create table for user responses
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_responses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                module_type TEXT NOT NULL,
                user_input TEXT,
                ai_feedback TEXT,
                score REAL DEFAULT 0,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
        print("Database initialized successfully")
        return True
    except Exception as e:
        print(f"Error initializing database: {str(e)}")
        return False

def save_user_response(session_id, module_type, user_input, ai_feedback, score=0):
    """Saves a user's response and AI feedback to the database."""
    try:
        conn = sqlite3.connect('user_data.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO user_responses 
            (session_id, module_type, user_input, ai_feedback, score, timestamp) 
            VALUES (?, ?, ?, ?, ?, datetime('now'))
        """, (session_id, module_type, user_input, ai_feedback, score))
        
        conn.commit()
        conn.close()
        print(f"Saved user response for session {session_id}, module {module_type}")
        return True
    except Exception as e:
        print(f"Error saving user response: {str(e)}")
        return False

def get_user_progress(session_id):
    """Retrieves all training responses for a user."""
    try:
        conn = sqlite3.connect('user_data.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Debug: Print query and session_id
        print(f"Executing query with session_id: {session_id}")
        
        cursor.execute("""
            SELECT module_type, user_input, ai_feedback, score, 
                   datetime(timestamp, 'localtime') as timestamp
            FROM user_responses
            WHERE session_id = ?
            ORDER BY timestamp DESC
        """, (session_id,))
        
        rows = cursor.fetchall()
        
        # Debug: Print number of rows retrieved
        print(f"Retrieved {len(rows)} rows from database")
        
        # Convert to list of dictionaries
        result = []
        for row in rows:
            result.append({
                'module_type': row['module_type'],
                'user_input': row['user_input'],
                'ai_feedback': row['ai_feedback'],
                'score': row['score'],
                'timestamp': row['timestamp']
            })
        
        conn.close()
        return result
    except Exception as e:
        print(f"Database error in get_user_progress: {str(e)}")
        return []