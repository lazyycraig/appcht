@echo off
REM Script untuk menjalankan Chat App dengan mudah

echo.
echo ╔═══════════════════════════════════════╗
echo ║  Chat Terenkripsi - Auto Launcher     ║
echo ╚═══════════════════════════════════════╝
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python tidak terinstall!
    echo Silakan download dari https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv" (
    echo 📦 Virtual environment belum ada, membuat...
    python -m venv venv
)

REM Activate virtual environment
echo ✅ Mengaktifkan virtual environment...
call venv\Scripts\activate.bat

REM Check if requirements are installed
pip show flask >nul 2>&1
if errorlevel 1 (
    echo 📥 Menginstall dependencies...
    pip install -q -r requirements.txt
    echo ✅ Dependencies terinstall
)

REM Run the app
echo.
echo 🚀 Menjalankan Chat App...
echo.
echo ╔═══════════════════════════════════════╗
echo ║  Buka: http://localhost:5000           ║
echo ║  Tekan CTRL+C untuk berhenti          ║
echo ╚═══════════════════════════════════════╝
echo.

python app.py

pause
