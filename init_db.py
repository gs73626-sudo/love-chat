import sqlite3

conn = sqlite3.connect("chat.db")
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sender TEXT NOT NULL,
    type TEXT NOT NULL,
    content TEXT NOT NULL,
    time TEXT NOT NULL
)
""")

conn.commit()
conn.close()

print("✅ SQLite 数据库初始化完成（chat.db）")
