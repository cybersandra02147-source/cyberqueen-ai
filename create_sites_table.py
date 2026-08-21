import sqlite3

DB = "users.db"

conn = sqlite3.connect(DB)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS sites (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    site_key TEXT UNIQUE NOT NULL,
    user_id INTEGER NOT NULL,
    job_id INTEGER NOT NULL,
    subscription_id INTEGER NOT NULL,
    folder TEXT NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    status TEXT DEFAULT 'ACTIVE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

conn.commit()
conn.close()

print("Sites table ready.")
