
import sqlite3
import json
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
DB_DIR = ROOT / "data"
DB_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DB_DIR / "polls.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_connection() as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS polls(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,
            options TEXT NOT NULL,
            active INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL
        )""")
        conn.execute("""CREATE TABLE IF NOT EXISTS votes(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            poll_id INTEGER NOT NULL,
            option TEXT NOT NULL,
            voter_token TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(poll_id) REFERENCES polls(id),
            UNIQUE(poll_id, voter_token)
        )""")
        conn.commit()

def _poll(row):
    d = dict(row)
    d["options"] = json.loads(d["options"])
    d["active"] = bool(d["active"])
    return d

def get_polls(active_only=False):
    sql = """SELECT p.*, COUNT(v.id) AS total_votes
             FROM polls p LEFT JOIN votes v ON p.id=v.poll_id"""
    if active_only:
        sql += " WHERE p.active=1"
    sql += " GROUP BY p.id ORDER BY p.created_at DESC"
    with get_connection() as conn:
        return [_poll(r) for r in conn.execute(sql).fetchall()]

def get_poll(poll_id):
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM polls WHERE id=?", (poll_id,)).fetchone()
        return _poll(row) if row else None

def create_poll(question, options):
    with get_connection() as conn:
        cur = conn.execute(
            "INSERT INTO polls(question, options, active, created_at) VALUES(?,?,1,?)",
            (question, json.dumps(options), datetime.now().isoformat(timespec="seconds"))
        )
        conn.commit()
        return cur.lastrowid

def vote(poll_id, option, voter_token):
    poll = get_poll(poll_id)
    if not poll or not poll["active"]:
        return False, "Poll is not active."
    if option not in poll["options"]:
        return False, "Invalid option."
    try:
        with get_connection() as conn:
            conn.execute(
                "INSERT INTO votes(poll_id, option, voter_token, created_at) VALUES(?,?,?,?)",
                (poll_id, option, voter_token, datetime.now().isoformat(timespec="seconds"))
            )
            conn.commit()
        return True, "Vote recorded successfully!"
    except sqlite3.IntegrityError:
        return False, "This voter token has already voted in this poll."

def get_results(poll_id):
    poll = get_poll(poll_id)
    if not poll:
        return []
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT option, COUNT(*) AS votes FROM votes WHERE poll_id=? GROUP BY option",
            (poll_id,)
        ).fetchall()
    counts = {r["option"]: r["votes"] for r in rows}
    return [{"option": o, "votes": counts.get(o, 0)} for o in poll["options"]]

def get_total_votes():
    with get_connection() as conn:
        return conn.execute("SELECT COUNT(*) FROM votes").fetchone()[0]

def get_recent_votes(limit=50):
    with get_connection() as conn:
        rows = conn.execute("""SELECT v.id, v.poll_id, p.question, v.option, v.created_at
            FROM votes v JOIN polls p ON p.id=v.poll_id
            ORDER BY v.id DESC LIMIT ?""", (limit,)).fetchall()
        return [dict(r) for r in rows]

def delete_poll(poll_id):
    with get_connection() as conn:
        conn.execute("DELETE FROM votes WHERE poll_id=?", (poll_id,))
        conn.execute("DELETE FROM polls WHERE id=?", (poll_id,))
        conn.commit()
