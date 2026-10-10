import sqlite3
from pathlib import Path
import pandas as pd

DB_PATH = Path(__file__).resolve().parent.parent / "coldguard.db"

def connect():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute("""CREATE TABLE IF NOT EXISTS alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        level TEXT NOT NULL,
        title TEXT NOT NULL,
        detail TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'Active',
        action TEXT DEFAULT ''
    )""")
    conn.commit()
    return conn

def add_alert(level, title, detail):
    conn = connect()
    conn.execute("INSERT INTO alerts(timestamp, level, title, detail, status) VALUES(datetime('now'), ?, ?, ?, 'Active')",
                 (level, title, detail))
    conn.commit()
    conn.close()

def get_alerts():
    conn = connect()
    df = pd.read_sql_query("SELECT * FROM alerts ORDER BY id DESC", conn)
    conn.close()
    return df

def update_alert(alert_id, status, action=""):
    conn = connect()
    conn.execute("UPDATE alerts SET status=?, action=? WHERE id=?", (status, action, int(alert_id)))
    conn.commit()
    conn.close()

def clear_alerts():
    conn = connect()
    conn.execute("DELETE FROM alerts")
    conn.commit()
    conn.close()
