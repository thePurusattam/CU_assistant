import sqlite3
from datetime import datetime
import os

DB_PATH = "data/chat_history.db"

def init_db():
    os.makedirs("data", exist_ok=True)
    con = sqlite3.connect(DB_PATH); c = con.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS sessions(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        created_at TEXT
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS messages(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id INTEGER,
        role TEXT,
        content TEXT,
        ts TEXT,
        FOREIGN KEY(session_id) REFERENCES sessions(id)
    )""")
    con.commit(); con.close()

def create_session(title="New Chat"):
    con = sqlite3.connect(DB_PATH); c = con.cursor()
    c.execute("INSERT INTO sessions (title, created_at) VALUES (?,?)",
              (title, datetime.now().isoformat()))
    con.commit()
    sid = c.lastrowid
    con.close()
    return sid

def list_sessions():
    con = sqlite3.connect(DB_PATH); c = con.cursor()
    rows = c.execute("SELECT id, title FROM sessions ORDER BY id DESC").fetchall()
    con.close(); return rows

def save_message(session_id, role, content):
    con = sqlite3.connect(DB_PATH); c = con.cursor()
    c.execute("INSERT INTO messages (session_id, role, content, ts) VALUES (?,?,?,?)",
              (session_id, role, content, datetime.now().isoformat()))
    con.commit(); con.close()

def get_messages(session_id):
    con = sqlite3.connect(DB_PATH); c = con.cursor()
    rows = c.execute("SELECT role, content FROM messages WHERE session_id=? ORDER BY id ASC",
                     (session_id,)).fetchall()
    con.close(); return rows

# --- Add these utilities to modules/database.py ---

def delete_session(session_id: int):
    """Delete a whole chat session and its messages."""
    con = sqlite3.connect(DB_PATH); c = con.cursor()
    # ensure foreign keys off? we delete explicitly:
    c.execute("DELETE FROM messages WHERE session_id=?", (session_id,))
    c.execute("DELETE FROM sessions WHERE id=?", (session_id,))
    con.commit(); con.close()

def rename_session(session_id: int, new_title: str):
    con = sqlite3.connect(DB_PATH); c = con.cursor()
    c.execute("UPDATE sessions SET title=? WHERE id=?", (new_title, session_id))
    con.commit(); con.close()
