# 🚀 Quick Start Guide - Chat Terenkripsi

## ⚡ Instalasi Cepat (5 Menit)

### Step 1: Buka Command Prompt/PowerShell

Masuk ke folder aplikasi:
```bash
cd d:\Iwang\MASTERAN_WB\program\PY\App_chat
```

### Step 2: Setup Environment Python

Buat virtual environment:
```bash
python -m venv venv
```

Aktifkan:
```bash
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

Tunggu sampai selesai (~ 2-3 menit)

### Step 4: Jalankan Aplikasi

```bash
python app.py
```

Akan muncul output:
```
 * Running on http://0.0.0.0:5000
 * Press CTRL+C to quit
```

### Step 5: Buka di Browser

Buka browser dan kunjungi:
```
http://localhost:5000
```

✅ Aplikasi siap digunakan!

---

## 📱 Testing Chat

### Scenario 1: Chat di Komputer Sama

1. Buka tab browser baru
2. Di tab 1: Buat chat room baru dengan nama "Alice"
3. Copy link yang muncul
4. Di tab 2: Kunjungi link tersebut dengan nama "Bob"
5. Chat antara keduanya!

### Scenario 2: Chat Komputer ke Mobile

1. Komputer: Buat chat room dan copy link
2. Cari IP komputer:
   ```bash
   ipconfig
   # Cari "IPv4 Address" (contoh: 192.168.1.5)
   ```
3. Mobile: Buka browser dan akses:
   ```
   http://192.168.1.5:5000
   ```
4. Paste link yang dikopy dari komputer
5. Chat antar perangkat!

### Scenario 3: Menggunakan QR Code

1. Komputer: Buat chat room
2. Scan QR code dengan mobile
3. Mobile otomatis buka link chat
4. Isi nama dan bergabung

---

## 🔐 Keamanan

✅ **Pesan dienkripsi** menggunakan AES-128 (Fernet)
✅ **Link unik** untuk setiap room (32 karakter random)
✅ **Tidak perlu login** - hanya butuh link
✅ **Online status real-time** via WebSocket
✅ **Session aman** dengan HTTPS cookie protection

---

## 🛑 Jika Ada Error

### Error: "Port 5000 already in use"
```bash
# Windows - Cari dan kill process
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Linux/Mac
lsof -i :5000
kill -9 <PID>
```

### Error: "Module not found"
```bash
# Pastikan virtual environment aktif
venv\Scripts\activate

# Install ulang
pip install -r requirements.txt
```

### Error: "Connection refused"
- Pastikan aplikasi sedang running
- Check apakah port 5000 tidak ada error
- Restart aplikasi

### Database Error
```bash
# Delete database lama
del chat.db

# Aplikasi akan membuat database baru otomatis
```

---

## 🔧 Customization

### Ubah Port

Edit baris terakhir di `app.py`:
```python
# Dari:
socketio.run(app, debug=True, host='0.0.0.0', port=5000)

# Menjadi:
socketio.run(app, debug=True, host='0.0.0.0', port=8000)  # Port baru
```

### Ubah Warna/Theme

Edit `static/css/style.css` bagian `:root`:
```css
:root {
    --primary-color: #2563eb;      /* Warna tombol utama */
    --secondary-color: #10b981;    /* Warna accent */
    --danger-color: #ef4444;       /* Warna error */
    --online: #10b981;             /* Warna online indicator */
    --offline: #94a3b8;            /* Warna offline indicator */
}
```

### Ubah Database

Default: SQLite
```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chat.db'
```

Untuk PostgreSQL:
```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@localhost/chatdb'
```

---

## 📊 Fitur yang Ada

### Chat Room Features
- ✅ Create room dengan link unik
- ✅ Join room via link
- ✅ QR code untuk sharing
- ✅ Histori pesan tersimpan
- ✅ Real-time messaging via WebSocket

### Security Features
- ✅ Pesan dienkripsi AES-128
- ✅ Link random 32 karakter
- ✅ Session management aman
- ✅ No login required
- ✅ Database encryption

### User Experience
- ✅ Mobile responsive design
- ✅ Online/offline indicator
- ✅ Real-time status update
- ✅ Beautiful UI dengan animasi
- ✅ Easy copy-paste link

---

## 🌐 Access dari Internet (Ngrok)

Jika ingin bagikan link ke orang lain di internet:

```bash
# Install ngrok
# https://ngrok.com/download

# Jalankan ngrok
ngrok http 5000

# Akan dapat URL public (contoh)
# https://abc123.ngrok.io

# Bagikan link chat room dengan format:
# https://abc123.ngrok.io/join/ACCESS_LINK
```

⚠️ **Note**: Ngrok free tier ada rate limit, untuk production gunakan VPS/server proper

---

## 💡 Tips & Tricks

1. **Backup Pesan**
   - Database disimpan di `chat.db`
   - Download/backup file ini untuk save chat history

2. **Multi Tab Testing**
   - Buka 2+ tab untuk test chat antar tab
   - Useful untuk development

3. **Browser Console**
   - Tekan F12 → Console untuk lihat WebSocket messages
   - Helpful untuk debugging

4. **Incognito Mode**
   - Gunakan incognito/private mode untuk test
   - Tidak ada cache dari session sebelumnya

---

## 📖 Next Steps

Setelah apps berjalan, Anda bisa:

1. **Deploy ke VPS**
   - Gunakan Gunicorn + Nginx
   - Setup SSL certificate

2. **Custom Domain**
   - Register domain
   - Point ke VPS Anda

3. **Add More Features**
   - File sharing
   - Voice/video call
   - Group chat
   - Message reactions

4. **Database Migration**
   - Switch ke PostgreSQL untuk production
   - Better performance & scalability

---

## 📞 Support & Troubleshooting

Jika stuck, cek:
1. ✅ Virtual environment aktif
2. ✅ Dependencies terinstall (`pip list`)
3. ✅ Port 5000 tidak digunakan apps lain
4. ✅ Flask app tidak ada error
5. ✅ Browser cache di-clear (F5 refresh)

---

**Happy Chatting! 💬**
