import sqlite3

conn = sqlite3.connect('instance/chat.db') # Sesuaikan nama file db Anda
cursor = conn.cursor()
try:
    cursor.execute("ALTER TABLE messages ADD COLUMN status INTEGER DEFAULT 1")
    conn.commit()
    print("✅ Kolom 'status' berhasil ditambahkan ke tabel messages.")
except sqlite3.OperationalError:
    print("ℹ️ Kolom 'status' sudah ada.")
conn.close()