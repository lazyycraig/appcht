# 🔧 Panduan Instalasi Lengkap

## ✅ Prerequisites (Syarat Sistem)

Sebelum install, pastikan Anda punya:

### 1. Python 3.8 atau lebih tinggi
```bash
# Check Python version
python --version
# Harus output: Python 3.8.x atau lebih tinggi
```

**Jika belum install Python:**
- Download dari https://www.python.org/downloads/
- Saat install, **CENTANG "Add Python to PATH"**
- Restart komputer setelah install

### 2. Windows / Linux / Mac
- Aplikasi ini berjalan di semua OS

### 3. Internet Connection
- Untuk download dependencies
- Pertama kali setup saja

### 4. ~50MB Disk Space
- Untuk virtual environment dan dependencies

---

## 📥 Installation Steps

### Step 1: Download/Clone Project

**Option A: Manual Download**
```bash
# Project sudah ada di:
# d:\Iwang\MASTERAN_WB\program\PY\App_chat
```

**Option B: Clone dari Git** (jika Anda punya Git)
```bash
git clone <repository-url>
cd App_chat
```

### Step 2: Buka Command Prompt/Terminal

**Windows:**
- Press: `Win + R`
- Type: `cmd`
- Press: Enter

**Linux/Mac:**
- Open Terminal application

### Step 3: Navigasi ke Folder Project

```bash
cd d:\Iwang\MASTERAN_WB\program\PY\App_chat
```

Atau di Mac/Linux:
```bash
cd /path/to/App_chat
```

**Verify:** Pastikan Anda bisa lihat file `app.py`
```bash
# Windows
dir app.py

# Linux/Mac
ls app.py
```

### Step 4: Buat Virtual Environment

Virtual environment adalah isolated Python workspace untuk project ini.

```bash
python -m venv venv
```

**Penjelasan:**
- `python` = Python interpreter
- `-m venv` = Module virtual environment
- `venv` = Nama folder untuk virtual environment

**Output:** Akan membuat folder `venv/` di project

### Step 5: Aktifkan Virtual Environment

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

**Verify:** Terminal akan tampak berbeda:
```
(venv) C:\path\to\App_chat>
```

atau

```
(venv) user@computer:~/App_chat$
```

### Step 6: Install Dependencies

```bash
pip install -r requirements.txt
```

**Apa yang dilakukan:**
- Membaca file `requirements.txt`
- Download semua library yang dibutuhkan
- Install ke virtual environment

**Progress:**
```
Collecting Flask==2.3.3
Downloading Flask-2.3.3-py3-none-any.whl (101 kB)
Installing collected packages: Werkzeug, Jinja2, click, Flask...
Successfully installed Flask-2.3.3
```

**Waktu:** 2-5 menit tergantung internet speed

**Jika error:**
```bash
# Clear pip cache
pip cache purge

# Try install again
pip install -r requirements.txt
```

### Step 7: Verify Installation

```bash
pip list
```

Pastikan semua ini ada dalam list:
- Flask
- Flask-SQLAlchemy
- Flask-SocketIO
- cryptography
- python-socketio
- python-engineio

---

## 🚀 Run Application

### Method 1: Auto Script (Recommended)

**Windows:**
1. Double-click: `run.bat`
2. Program akan start otomatis

**Linux/Mac:**
```bash
chmod +x run.sh
./run.sh
```

### Method 2: Manual Command

```bash
# Make sure venv is activated
venv\Scripts\activate  # Windows
# or
source venv/bin/activate  # Linux/Mac

# Run the app
python app.py
```

### Success Output

Jika berhasil, Anda akan melihat:

```
 * Running on http://0.0.0.0:5000
 * Debug mode: on
 * WARNING in app.run_once_with_reloader - This is a development server...
 Press CTRL+C to quit
```

---

## 🌐 Access Application

### Local Computer

Open browser dan buka:
```
http://localhost:5000
```

atau

```
http://127.0.0.1:5000
```

### Different Computer (Same Network)

1. Find your computer IP:

**Windows:**
```bash
ipconfig
# Find: "IPv4 Address" (ex: 192.168.1.100)
```

**Linux/Mac:**
```bash
ifconfig
# Find: "inet addr" atau "inet"
```

2. On other computer, open:
```
http://192.168.1.100:5000
```

(Ganti 192.168.1.100 dengan IP Anda)

### Mobile Phone (Same WiFi)

1. Both devices harus connect ke WiFi sama
2. Get computer IP (lihat di atas)
3. Open browser di mobile:
```
http://192.168.x.x:5000
```

---

## ✅ Verify Installation

Setelah aplikasi running, test:

### Test 1: Homepage Loading
- Open: http://localhost:5000
- Should see: Form untuk create chat room
- Should see: "Chat Terenkripsi" heading

### Test 2: Create Room
- Enter name: "TestUser"
- Click: "Buat Chat Room Baru"
- Should see: Link dan QR code

### Test 3: Join Room
- Copy link dari step sebelumnya
- Open link di new tab
- Enter name: "TestUser2"
- Click: "Bergabung ke Chat"
- Should see: Chat interface

### Test 4: Send Message
- Type message: "Hello"
- Click send button
- Message should appear in chat
- Check both tabs

### Test 5: Online Status
- Should see: Green dot (online indicator)
- Close one tab
- Should see: Gray dot (offline)
- Open tab lagi
- Should see: Green dot again

---

## 📁 Project Structure Explained

```
App_chat/
├── app.py                    # Main server application
├── requirements.txt          # List of dependencies
├── .env.example             # Environment template
├── .gitignore               # Git ignore file
├── venv/                    # Virtual environment (auto-created)
│
├── README.md                # Full documentation
├── QUICK_START.md           # Quick start guide
├── TECHNICAL.md             # Technical details
├── PROJECT_SUMMARY.md       # Project summary
├── INSTALL.md               # This file
│
├── run.bat                  # Auto launcher for Windows
├── run.sh                   # Auto launcher for Linux/Mac
│
├── chat.db                  # Database (auto-created)
│
├── static/
│   ├── css/
│   │   └── style.css        # Styling
│   └── js/
│       └── index.js         # Frontend JavaScript
│
└── templates/
    ├── index.html           # Home page
    ├── join.html            # Join room page
    ├── chat.html            # Chat interface
    └── error.html           # Error page
```

---

## 🛑 Common Issues & Solutions

### Issue 1: "Python is not recognized"

**Cause:** Python tidak di PATH

**Solution:**
```bash
# Use full path to Python
C:\Users\YourName\AppData\Local\Programs\Python\Python311\python.exe -m venv venv
```

atau

- Reinstall Python
- **CENTANG "Add Python to PATH"** saat install
- Restart komputer

### Issue 2: "ModuleNotFoundError: No module named 'flask'"

**Cause:** Virtual environment tidak aktif

**Solution:**
```bash
# Activate venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Install again
pip install -r requirements.txt
```

### Issue 3: "Address already in use"

**Cause:** Port 5000 sedang digunakan

**Solution:**

**Windows:**
```bash
# Find process using port 5000
netstat -ano | findstr :5000

# Kill the process (replace XXXX with PID)
taskkill /PID XXXX /F

# Or use different port
# Edit app.py last line:
# socketio.run(app, debug=True, port=8000)
```

**Linux/Mac:**
```bash
# Find process
lsof -i :5000

# Kill process
kill -9 <PID>
```

### Issue 4: "Database is locked"

**Cause:** Database corruption

**Solution:**
```bash
# Delete old database
del chat.db  # Windows
rm chat.db   # Linux/Mac

# App akan create database baru otomatis
```

### Issue 5: "WebSocket connection failed"

**Cause:** Firewall blocking WebSocket

**Solution:**
- Check firewall settings
- Allow Python through firewall
- Try access from localhost first
- Restart app

### Issue 6: "QRCode not showing"

**Cause:** JavaScript error atau CDN tidak loading

**Solution:**
- Refresh browser
- Check internet connection
- Open browser console (F12)
- Look for error messages

### Issue 7: "Encrypted message shows gibberish"

**This is NORMAL!** 

Pesan di database emang encrypted (terlihat gibberish).
Saat user view, browser decrypt otomatis.

Verify:
- Open chat.db dengan SQLite
- Messages terlihat encrypted ✅
- Refresh browser
- Message terlihat normal ✅

---

## 🔄 Troubleshooting Checklist

Jika aplikasi bermasalah:

- [ ] Python terinstall? → `python --version`
- [ ] Venv aktif? → Terminal menunjukkan `(venv)`?
- [ ] Dependencies installed? → `pip list` punya Flask?
- [ ] Port 5000 free? → `netstat -ano | findstr :5000`
- [ ] Browser refreshed? → `Ctrl+F5`
- [ ] Console errors? → `F12` → Console tab
- [ ] Database intact? → `chat.db` exists?
- [ ] Network firewall? → Check security software

---

## 🔄 Restart Aplikasi

Jika perlu restart:

**Windows:**
```bash
# Stop current app
Press CTRL+C

# Deactivate venv
deactivate

# Activate kembali
venv\Scripts\activate

# Run lagi
python app.py
```

**Linux/Mac:**
```bash
# Stop current app
Press CTRL+C

# Activate venv
source venv/bin/activate

# Run lagi
python app.py
```

---

## 📖 Next Steps

Setelah instalasi berhasil:

1. **Read QUICK_START.md**
   - Testing scenarios
   - Tips & tricks

2. **Explore TECHNICAL.md**
   - Architecture overview
   - API documentation
   - Security details

3. **Customize**
   - Edit CSS untuk colors
   - Add your branding
   - Modify messages

4. **Deploy**
   - Setup production server
   - Configure HTTPS
   - Deploy to VPS

---

## ⭐ Tips untuk Instalasi Lancar

1. **Use Fresh Terminal**
   - Close semua terminal lama
   - Open terminal baru

2. **Use Absolute Paths**
   - Jangan gunakan relative paths
   - Gunakan full path: `C:\...\App_chat`

3. **Check Internet**
   - Download dependencies butuh internet
   - Pastikan koneksi stabil

4. **One Step at a Time**
   - Jangan skip steps
   - Verify setiap step berhasil

5. **Read Error Messages**
   - Error messages penting!
   - Google error message jika stuck

---

## 📞 Still Having Issues?

1. **Check README.md**
   - Lebih detail documentation

2. **Check TECHNICAL.md**
   - Troubleshooting section

3. **Check Python Docs**
   - https://docs.python.org/

4. **Check Flask Docs**
   - https://flask.palletsprojects.com/

5. **Stack Overflow**
   - Search error message Anda

---

## ✅ Installation Complete!

Jika Anda sampai sini tanpa error, **Selamat! 🎉**

Aplikasi Chat Terenkripsi siap digunakan!

**Langkah selanjutnya:**
1. Buka http://localhost:5000
2. Create chat room
3. Test dengan teman
4. Enjoy secure chatting! 💬🔐

---

**Last Updated: 2026-05-25**
**Installation Version: 1.0**
