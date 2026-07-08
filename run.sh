#!/bin/bash

# Script untuk menjalankan Chat App dengan mudah (Linux/Mac)

echo ""
echo "╔═══════════════════════════════════════╗"
echo "║  Chat Terenkripsi - Auto Launcher     ║"
echo "╚═══════════════════════════════════════╝"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 tidak terinstall!"
    echo "Silakan install dengan: brew install python3 (Mac) atau apt install python3 (Linux)"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Virtual environment belum ada, membuat..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "✅ Mengaktifkan virtual environment..."
source venv/bin/activate

# Check if requirements are installed
if ! pip show flask &> /dev/null; then
    echo "📥 Menginstall dependencies..."
    pip install -q -r requirements.txt
    echo "✅ Dependencies terinstall"
fi

# Run the app
echo ""
echo "🚀 Menjalankan Chat App..."
echo ""
echo "╔═══════════════════════════════════════╗"
echo "║  Buka: http://localhost:5000           ║"
echo "║  Tekan CTRL+C untuk berhenti          ║"
echo "╚═══════════════════════════════════════╝"
echo ""

python3 app.py
