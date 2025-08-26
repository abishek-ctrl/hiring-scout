import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "hiring_scout.db")

def init_db():
    """Initialize SQLite DB with tables for sessions, messages, and evaluations."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            privacy_accepted INTEGER DEFAULT 0
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER,
            role TEXT,
            content TEXT,
            FOREIGN KEY(session_id) REFERENCES sessions(id)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS evaluations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER UNIQUE,
            full_name TEXT,
            email TEXT,
            phone TEXT,
            summary TEXT,
            strengths TEXT,
            weaknesses TEXT,
            score INTEGER,
            FOREIGN KEY(session_id) REFERENCES sessions(id)
        )
    """)
    conn.commit()
    conn.close()

def create_session():
    """Create a new session and return its ID."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO sessions (privacy_accepted) VALUES (0)")
    conn.commit()
    session_id = cursor.lastrowid
    conn.close()
    return session_id

def get_session(session_id):
    """Return session data by ID."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, privacy_accepted FROM sessions WHERE id=?", (session_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {"id": row[0], "privacy_accepted": bool(row[1])}
    return None

def set_privacy_accepted(session_id, accepted=True):
    """Update session with privacy acceptance."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE sessions SET privacy_accepted=? WHERE id=?", (1 if accepted else 0, session_id))
    conn.commit()
    conn.close()

def save_message(session_id, role, content):
    """Save a message in the DB for a session."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO messages (session_id, role, content) VALUES (?, ?, ?)", (session_id, role, content))
    conn.commit()
    conn.close()

def load_messages(session_id):
    """Load all messages for a session."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT role, content FROM messages WHERE session_id=?", (session_id,))
    rows = cursor.fetchall()
    conn.close()
    return [{"role": r[0], "content": r[1]} for r in rows]

def clear_session(session_id):
    """Delete all messages for a session (GDPR right-to-erasure)."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM messages WHERE session_id=?", (session_id,))
    conn.commit()
    conn.close()

def save_evaluation(session_id, full_name, email, phone, summary, strengths, weaknesses, score):
    """Save a candidate evaluation in the DB for a session."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO evaluations (session_id, full_name, email, phone, summary, strengths, weaknesses, score) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (session_id, full_name, email, phone, summary, strengths, weaknesses, score))
    conn.commit()
    conn.close()