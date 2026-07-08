import sqlite3

def migrate():
    # Sesuaikan dengan nama file database .db Anda jika berbeda
    db_path = 'instance/chat.db' 
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("Memulai migrasi database...")
    
    # Tambah kolom baru ke tabel messages secara manual
    columns_to_add = [
        ("parent_id", "INTEGER"),
        ("parent_sender_name", "VARCHAR(100)"),
        ("parent_content", "TEXT")
    ]
    
    for col_name, col_type in columns_to_add:
        try:
            cursor.execute(f"ALTER TABLE messages ADD COLUMN {col_name} {col_type}")
            print(f"✅ Kolom '{col_name}' berhasil ditambahkan.")
        except sqlite3.OperationalError:
            print(f"ℹ️ Kolom '{col_name}' sudah ada, dilewati.")
            
    conn.commit()
    conn.close()
    print("Migrasi selesai! Silakan jalankan kembali app Anda.")

if __name__ == '__main__':
    migrate()