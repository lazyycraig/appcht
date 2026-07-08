import os
import secrets
import json
from datetime import datetime
from functools import wraps
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit, join_room, leave_room
from werkzeug.security import generate_password_hash, check_password_hash
from cryptography.fernet import Fernet
import base64
import hashlib
from werkzeug.utils import secure_filename
import io

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', secrets.token_hex(32))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chat.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Session security: disable secure flag in development (HTTP)
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production (HTTPS)
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Initialize extensions
db = SQLAlchemy(app)
socketio = SocketIO(app, cors_allowed_origins="*", engineio_logger=False, logger=False)

# Upload settings
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp','mp4', 'mov', 'avi', 'mkv', 'flv', 'wmv'}
UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Store online users
online_users = {}

# ============================================================================
# DATABASE MODELS
# ============================================================================

class ChatRoom(db.Model):
    __tablename__ = 'chat_rooms'
    
    id = db.Column(db.String(36), primary_key=True)
    access_link = db.Column(db.String(255), unique=True, nullable=False)
    encryption_key = db.Column(db.String(255), nullable=False)
    user1_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)
    user2_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)
    user1_name = db.Column(db.String(100), nullable=False)
    user2_name = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    messages = db.relationship('Message', backref='room', lazy=True, cascade='all, delete-orphan')
    user1 = db.relationship('User', foreign_keys=[user1_id], backref='created_rooms')
    user2 = db.relationship('User', foreign_keys=[user2_id], backref='joined_rooms')
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.id = str(secrets.token_hex(8))
        self.access_link = secrets.token_urlsafe(32)
        self.encryption_key = Fernet.generate_key().decode()


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.String(36), primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, username, password):
        self.id = str(secrets.token_hex(8))
        self.username = username
        self.password_hash = generate_password_hash(password)
    
    def get_rooms(self):
        """Get all rooms where user is either creator or participant"""
        return ChatRoom.query.filter(
            (ChatRoom.user1_id == self.id) | (ChatRoom.user2_id == self.id)
        ).order_by(ChatRoom.created_at.desc()).all()


class Message(db.Model):
    __tablename__ = 'messages'
    
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.String(36), db.ForeignKey('chat_rooms.id'), nullable=False)
    sender_id = db.Column(db.String(36), nullable=False)
    sender_name = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    is_encrypted = db.Column(db.Boolean, default=True)
    message_type = db.Column(db.String(20), default='text')
    message_mime = db.Column(db.String(50), nullable=True)

    # FITUR INDIKATOR STATUS PESAN (1: Centang 1, 2: Centang 2 Abu-abu, 3: Centang 2 Biru)
    status = db.Column(db.Integer, default=1, nullable=False)

    # FITUR RELASI REPLY / BALASAN PESAN
    parent_id = db.Column(db.Integer, db.ForeignKey('messages.id', ondelete='SET NULL'), nullable=True)
    parent_sender_name = db.Column(db.String(100), nullable=True)
    parent_content = db.Column(db.Text, nullable=True)  # Content terenkripsi/teks penanda media terpaut


# ============================================================================
# ENCRYPTION UTILITIES
# ============================================================================

def encrypt_message(message_text, key_str):
    """Encrypt message using Fernet"""
    try:
        f = Fernet(key_str.encode() if isinstance(key_str, str) else key_str)
        encrypted = f.encrypt(message_text.encode())
        return encrypted.decode()
    except Exception as e:
        print(f"Encryption error: {e}")
        return message_text

def decrypt_message(encrypted_text, key_str):
    """Decrypt message using Fernet"""
    try:
        f = Fernet(key_str.encode() if isinstance(key_str, str) else key_str)
        decrypted = f.decrypt(encrypted_text.encode())
        return decrypted.decode()
    except Exception as e:
        print(f"Decryption error: {e}")
        return "[Unable to decrypt message]"

# ============================================================================
# ROUTES
# ============================================================================

@app.route('/')
def index():
    """Home page - create new chat room"""
    return redirect(url_for('dashboard'))

@app.route('/create-room', methods=['POST'])
def create_room():
    """Create a new chat room"""
    try:
        data = request.get_json()
        name = data.get('name', '').strip()
        
        if not name or len(name) < 2:
            return jsonify({'error': 'Nama harus minimal 2 karakter'}), 400
        
        if 'user_id' in session:
            creator_id = session['user_id']
            creator_name = session.get('user_name', name)
        else:
            creator_id = secrets.token_hex(8)
            creator_name = name

        room = ChatRoom(user1_name=creator_name, user1_id=creator_id)
        db.session.add(room)
        db.session.commit()

        session['user_id'] = creator_id
        session['user_name'] = creator_name
        session['room_id'] = room.id
        session['is_creator'] = True
        session.modified = True
        
        return jsonify({
            'room_id': room.id,
            'access_link': room.access_link,
            'status': 'created'
        })
    except Exception as e:
        print(f"Error creating room: {e}")
        return jsonify({'error': 'Gagal membuat room'}), 500

@app.route('/join/<link>')
def join_chat(link):
    """Join a chat room via access link"""
    try:
        room = ChatRoom.query.filter_by(access_link=link).first()
        if not room:
            return render_template('error.html', message='Link chat tidak valid atau sudah expired')
        
        if room.user2_id is not None:
            return render_template('error.html', message='Chat room sudah penuh (2 orang)')
        
        return render_template('join.html', room_id=room.id, access_link=link)
    except Exception as e:
        print(f"Error joining chat: {e}")
        return render_template('error.html', message='Terjadi kesalahan')


@app.route('/join')
def join_root():
    """Render join page without a prefilled link (user can paste link)."""
    return render_template('join.html', room_id=None, access_link='')

@app.route('/join-room', methods=['POST'])
def join_room_post():
    """Handle join room request"""
    try:
        data = request.get_json()
        name = data.get('name', '').strip()
        access_link = data.get('access_link', '').strip()
        
        if not name or len(name) < 2:
            return jsonify({'error': 'Nama harus minimal 2 karakter'}), 400
        
        room = ChatRoom.query.filter_by(access_link=access_link).first()
        if not room:
            return jsonify({'error': 'Link tidak valid'}), 404
        
        if room.user2_id is not None:
            return jsonify({'error': 'Chat room sudah penuh'}), 400
        
        if 'user_id' in session:
            room.user2_id = session['user_id']
            room.user2_name = session.get('user_name', name)
        else:
            room.user2_id = secrets.token_hex(8)
            room.user2_name = name
        db.session.commit()
        
        session['user_id'] = room.user2_id
        session['user_name'] = name
        session['room_id'] = room.id
        session['is_creator'] = False
        
        return jsonify({
            'room_id': room.id,
            'status': 'joined'
        })
    except Exception as e:
        print(f"Error joining room: {e}")
        return jsonify({'error': 'Gagal bergabung room'}), 500


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')

    data = request.get_json() if request.is_json else request.form
    username = data.get('username', '').strip()
    password = data.get('password', '')

    if not username or not password:
        return jsonify({'error': 'Username dan password diperlukan'}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username sudah digunakan'}), 400

    try:
        user = User(username, password)
        db.session.add(user)
        db.session.commit()

        session['user_id'] = user.id
        session['user_name'] = user.username

        return jsonify({'status': 'registered', 'user_id': user.id})
    except Exception as e:
        print(f"Error registering user: {e}")
        return jsonify({'error': 'Gagal mendaftar'}), 500


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    data = request.get_json() if request.is_json else request.form
    username = data.get('username', '').strip()
    password = data.get('password', '')

    if not username or not password:
        return jsonify({'error': 'Username dan password diperlukan'}), 400

    user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({'error': 'Username atau password salah'}), 401

    session['user_id'] = user.id
    session['user_name'] = user.username

    return jsonify({'status': 'logged_in', 'user_id': user.id})


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    """User dashboard - shows room history"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    if not user:
        session.clear()
        return redirect(url_for('login'))
    
    rooms = user.get_rooms()
    return render_template('dashboard.html', user=user, rooms=rooms)

@app.route('/api/user/rooms')
def api_user_rooms():
    """API endpoint to get user's room history"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    user = User.query.get(session['user_id'])
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    rooms = user.get_rooms()
    rooms_data = []
    
    for room in rooms:
        last_message = Message.query.filter_by(room_id=room.id).order_by(Message.timestamp.desc()).first()
        last_msg_text = None
        last_msg_time = None
        if last_message:
            if getattr(last_message, 'message_type', 'text') == 'image':
                last_msg_text = '/media/' + str(last_message.content)
            else:
                last_msg_text = decrypt_message(last_message.content, room.encryption_key) if last_message.is_encrypted else last_message.content
            last_msg_time = last_message.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        
        other_user = room.user2_name if room.user1_id == user.id else room.user1_name
        
        rooms_data.append({
            'room_id': room.id,
            'access_link': room.access_link,
            'name': f"Chat dengan {other_user}" if other_user else "Chat Room",
            'other_user': other_user,
            'created_at': room.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'last_message': last_msg_text,
            'last_message_time': last_msg_time,
            'message_count': len(room.messages),
            'is_creator': (room.user1_id == user.id)
        })
    
    return jsonify({'rooms': rooms_data})


@app.route('/api/room/<room_id>', methods=['DELETE'])
def api_delete_room(room_id):
    """Delete a chat room and its messages/uploads. Only participants can delete."""
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401

    room = ChatRoom.query.get(room_id)
    if not room:
        return jsonify({'error': 'Room not found'}), 404

    user_id = session.get('user_id')
    if user_id not in (room.user1_id, room.user2_id):
        return jsonify({'error': 'Unauthorized'}), 403

    messages = Message.query.filter_by(room_id=room_id).all()
    for m in messages:
        try:
            if getattr(m, 'message_type', 'text') == 'image':
                token = m.content
                if token:
                    enc_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{token}.enc")
                    if os.path.exists(enc_path):
                        try:
                            os.remove(enc_path)
                        except Exception:
                            pass
        except Exception:
            pass

    try:
        db.session.delete(room)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete room'}), 500

    return jsonify({'status': 'deleted'})

@app.route('/chat/<room_id>')
def chat(room_id):
    """Chat page"""
    room = ChatRoom.query.get(room_id)
    if not room:
        return render_template('error.html', message='Room tidak ditemukan')
    
    current_user_id = session.get('user_id')
    session_room_id = session.get('room_id')
    
    if not current_user_id:
        if session_room_id != room_id:
            return redirect(url_for('index'))
    else:
        is_user1 = current_user_id == room.user1_id
        is_user2 = current_user_id == room.user2_id
        has_room_session = session_room_id == room_id
        
        if not (is_user1 or is_user2 or has_room_session):
            return redirect(url_for('index'))
        
        session['room_id'] = room_id
        session.modified = True
        
        if is_user1:
            session['user_name'] = room.user1_name
            session['is_creator'] = True
        elif is_user2:
            session['user_name'] = room.user2_name
            session['is_creator'] = False
    
    # KETIKA MEMBUKA CHAT: Otomatis tandai pesan dari lawan bicara sebagai "Telah Dibaca" (status=3)
    unread_messages = Message.query.filter_by(room_id=room_id).filter(Message.sender_id != current_user_id, Message.status < 3).all()
    if unread_messages:
        for msg in unread_messages:
            msg.status = 3
        db.session.commit()
        # Beritahu lawan lewat WebSocket jika mereka terhubung
        socketio.emit('messages_read_update', {'room_id': room_id}, room=room_id)

    messages = Message.query.filter_by(room_id=room_id).all()
    decrypted_messages = []
    
    for msg in messages:
        msg_type = getattr(msg, 'message_type', 'text')
        if msg_type == 'image':
            if isinstance(msg.content, str) and (msg.content.startswith('/') or msg.content.startswith('http')):
                content = msg.content
            else:
                content = url_for('media', token=msg.content)
        else:
            content = decrypt_message(msg.content, room.encryption_key) if msg.is_encrypted else msg.content

        parent_content_decrypted = None
        if msg.parent_id:
            if msg.parent_content:
                if str(msg.parent_content).startswith('📷'):
                    parent_content_decrypted = msg.parent_content
                else:
                    parent_content_decrypted = decrypt_message(msg.parent_content, room.encryption_key)
            else:
                parent_content_decrypted = "Pesan telah dihapus"

        try:
            iso_ts = msg.timestamp.replace(microsecond=0).isoformat() + 'Z'
        except Exception:
            iso_ts = msg.timestamp.strftime('%H:%M:%S')

        decrypted_messages.append({
            'id': msg.id,
            'sender_name': msg.sender_name,
            'sender_id': msg.sender_id,
            'content': content,
            'timestamp': iso_ts,
            'type': msg_type,
            'status': msg.status,  # Kirim status pesan ke UI
            'parent_id': msg.parent_id,
            'parent_sender_name': msg.parent_sender_name,
            'parent_content': parent_content_decrypted
        })
    
    other_user = None
    if session.get('is_creator') and room.user2_name:
        other_user = room.user2_name
    elif not session.get('is_creator') and room.user1_name:
        other_user = room.user1_name
    
    return render_template('chat.html',
        room_id=room_id,
        user_name=session.get('user_name'),
        user_id=session.get('user_id'),
        other_user=other_user,
        messages=decrypted_messages
    )

@app.route('/api/room-status/<room_id>', methods=['GET'])
def room_status(room_id):
    """Get room status (who's online)"""
    room = ChatRoom.query.get(room_id)
    if not room:
        return jsonify({'error': 'Room tidak ditemukan'}), 404
    
    user1_online = room.user1_id in online_users
    user2_online = room.user2_id in online_users if room.user2_id else False
    
    return jsonify({
        'user1_online': user1_online,
        'user1_name': room.user1_name,
        'user2_online': user2_online,
        'user2_name': room.user2_name or 'Menunggu...',
        'room_full': room.user2_id is not None
    })

# ============================================================================
# WEBSOCKET EVENTS
# ============================================================================

@socketio.on('user_join')
def handle_user_join(data):
    """Handle user joining a room"""
    user_id = data.get('user_id')
    room_id = data.get('room_id')
    user_name = data.get('user_name')
    
    if user_id and room_id:
        online_users[user_id] = {
            'room_id': room_id,
            'user_name': user_name,
            'connected_at': datetime.utcnow()
        }
        join_room(room_id)
        
        # SINKRONISASI ONLINE: Jika lawan masuk room, update semua pesan belum terbaca di room ini menjadi Terbaca (3)
        unread_messages = Message.query.filter_by(room_id=room_id).filter(Message.sender_id != user_id, Message.status < 3).all()
        if unread_messages:
            for msg in unread_messages:
                msg.status = 3
            db.session.commit()
            emit('messages_read_update', {'room_id': room_id}, room=room_id)

        emit('user_status_changed', {
            'user_id': user_id,
            'user_name': user_name,
            'online': True
        }, room=room_id)

@socketio.on('disconnect')
def handle_disconnect():
    for user_id in list(online_users.keys()):
        try:
            room_id = online_users[user_id].get('room_id')
            user_name = online_users[user_id].get('user_name')
            # Hapus dari list online jika terputus
            del online_users[user_id]
            
            emit('user_status_changed', {
                'user_id': user_id,
                'user_name': user_name,
                'online': False
            }, room=room_id)
        except:
            pass

@socketio.on('read_messages')
def handle_read_messages(data):
    """Event manual ketika user aktif fokus di jendela chat room"""
    room_id = data.get('room_id')
    user_id = data.get('user_id')
    
    if room_id and user_id:
        unread = Message.query.filter_by(room_id=room_id).filter(Message.sender_id != user_id, Message.status < 3).all()
        if unread:
            for msg in unread:
                msg.status = 3
            db.session.commit()
            emit('messages_read_update', {'room_id': room_id}, room=room_id)

@socketio.on('send_message')
def handle_message(data):
    """Handle incoming message"""
    try:
        room_id = data.get('room_id')
        user_id = data.get('user_id')
        user_name = data.get('user_name')
        content = data.get('content', '').strip()
        parent_id = data.get('parent_id')
        
        if not content or not room_id or not user_id:
            emit('error', {'message': 'Data tidak lengkap'})
            return
        
        room = ChatRoom.query.get(room_id)
        if not room:
            emit('error', {'message': 'Room tidak ditemukan'})
            return
        
        # LOGIKA DETEKSI CENTANG (1 ATAU 2) SECARA REALTIME
        # Cari tahu id lawan bicara di room ini
        other_user_id = room.user2_id if user_id == room.user1_id else room.user1_id
        
        # Default Status 1 (Centang 1: Dikirim ke Server)
        msg_status = 1 
        
        if other_user_id:
            # Cek apakah lawan saat ini sedang terhubung dan berada di dalam room yang sama
            is_other_user_online = other_user_id in online_users
            is_in_same_room = online_users.get(other_user_id, {}).get('room_id') == room_id if is_other_user_online else False
            
            if is_in_same_room:
                msg_status = 3  # Langsung Centang 2 Biru (karena sedang buka obrolan)
            elif is_other_user_online:
                msg_status = 2  # Centang 2 Abu-abu (lawan online di dashboard/aplikasi tapi belum buka room)

        encrypted_content = encrypt_message(content, room.encryption_key)
        
        p_sender_name = None
        p_content_encrypted = None
        broadcast_parent_preview = None
        
        if parent_id:
            parent_msg = Message.query.get(parent_id)
            if parent_msg:
                p_sender_name = parent_msg.sender_name
                if getattr(parent_msg, 'message_type', 'text') == 'image':
                    p_content_encrypted = "📷 [Foto]"
                    broadcast_parent_preview = "📷 [Foto]"
                else:
                    p_content_encrypted = parent_msg.content
                    broadcast_parent_preview = decrypt_message(parent_msg.content, room.encryption_key) if parent_msg.is_encrypted else parent_msg.content

        # Simpan pesan dengan status yang sudah divalidasi
        message = Message(
            room_id=room_id,
            sender_id=user_id,
            sender_name=user_name,
            content=encrypted_content,
            is_encrypted=True,
            status=msg_status,
            parent_id=parent_id,
            parent_sender_name=p_sender_name,
            parent_content=p_content_encrypted
        )
        db.session.add(message)
        db.session.commit()
        
        try:
            out_ts = message.timestamp.replace(microsecond=0).isoformat() + 'Z'
        except Exception:
            out_ts = message.timestamp.strftime('%H:%M:%S')

        emit('new_message', {
            'id': message.id,
            'sender_name': user_name,
            'sender_id': user_id,
            'content': content,
            'timestamp': out_ts,
            'type': 'text',
            'status': msg_status, # Sertakan status ter-update saat broadcast
            'parent_id': parent_id,
            'parent_sender_name': p_sender_name,
            'parent_content': broadcast_parent_preview
        }, room=room_id)
        
    except Exception as e:
        print(f"Error handling message: {e}")
        emit('error', {'message': 'Gagal mengirim pesan'})

@socketio.on('check_online')
def handle_check_online(data):
    """Check if other user is online"""
    room_id = data.get('room_id')
    
    room = ChatRoom.query.get(room_id)
    if room:
        user1_online = room.user1_id in online_users
        user2_online = room.user2_id in online_users if room.user2_id else False
        
        emit('online_status', {
            'user1_online': user1_online,
            'user2_online': user2_online
        }, room=room_id)


@app.route('/upload-photo', methods=['POST'])
def upload_photo():
    """Handle photo uploads from clients and emit image messages."""
    try:
        if 'photo' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400

        file = request.files['photo']
        room_id = request.form.get('room_id')
        user_id = request.form.get('user_id')
        user_name = request.form.get('user_name')
        parent_id = request.form.get('parent_id')

        if not file or file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        if not room_id or not user_id:
            return jsonify({'error': 'Missing room or user info'}), 400

        filename = secure_filename(file.filename)
        if '.' in filename:
            ext = filename.rsplit('.', 1)[1].lower()
        else:
            ext = ''

        if ext not in ALLOWED_EXTENSIONS:
            return jsonify({'error': 'File type not allowed'}), 400

        room = ChatRoom.query.get(room_id)
        if not room:
            return jsonify({'error': 'Room not found'}), 404

        file_bytes = file.read()
        try:
            key = room.encryption_key
            f = Fernet(key.encode() if isinstance(key, str) else key)
            encrypted_bytes = f.encrypt(file_bytes)
        except Exception as e:
            print('Encryption error for upload:', e)
            return jsonify({'error': 'Encryption failed'}), 500

        token = secrets.token_hex(16)
        enc_name = f"{token}.enc"
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], enc_name)
        with open(save_path, 'wb') as fh:
            fh.write(encrypted_bytes)

        # LOGIKA DETEKSI STATUS ATRIBUT UNTUK FILE GAMBAR
        other_user_id = room.user2_id if user_id == room.user1_id else room.user1_id
        msg_status = 1
        if other_user_id:
            is_other_user_online = other_user_id in online_users
            is_in_same_room = online_users.get(other_user_id, {}).get('room_id') == room_id if is_other_user_online else False
            if is_in_same_room:
                msg_status = 3
            elif is_other_user_online:
                msg_status = 2

        p_sender_name = None
        p_content_encrypted = None
        broadcast_parent_preview = None
        if parent_id:
            parent_msg = Message.query.get(parent_id)
            if parent_msg:
                p_sender_name = parent_msg.sender_name
                if getattr(parent_msg, 'message_type', 'text') == 'image':
                    p_content_encrypted = "📷 [Foto]"
                    broadcast_parent_preview = "📷 [Foto]"
                else:
                    p_content_encrypted = parent_msg.content
                    broadcast_parent_preview = decrypt_message(parent_msg.content, room.encryption_key) if parent_msg.is_encrypted else parent_msg.content

        message = Message(
            room_id=room_id,
            sender_id=user_id,
            sender_name=user_name,
            content=token,
            is_encrypted=False,
            message_type='image',
            message_mime=file.mimetype or f'image/{ext}',
            status=msg_status,
            parent_id=parent_id if parent_id else None,
            parent_sender_name=p_sender_name,
            parent_content=p_content_encrypted
        )
        db.session.add(message)
        db.session.commit()

        file_url = url_for('media', token=token)
        try:
            out_ts = message.timestamp.replace(microsecond=0).isoformat() + 'Z'
        except Exception:
            out_ts = message.timestamp.strftime('%H:%M:%S')

        socketio.emit('new_message', {
            'id': message.id,
            'sender_name': user_name,
            'sender_id': user_id,
            'content': file_url,
            'timestamp': out_ts,
            'type': 'image',
            'status': msg_status,
            'parent_id': message.parent_id,
            'parent_sender_name': p_sender_name,
            'parent_content': broadcast_parent_preview
        }, room=room_id)

        return jsonify({'status': 'ok', 'url': file_url})
    except Exception as e:
        print(f"Upload error: {e}")
        return jsonify({'error': 'Gagal mengunggah foto'}), 500


@app.route('/media/<token>')
def media(token):
    """Decrypt and stream an uploaded image identified by token."""
    try:
        msg = Message.query.filter_by(content=token, message_type='image').order_by(Message.id.desc()).first()
        if not msg:
            return "Not found", 404

        room = ChatRoom.query.get(msg.room_id)
        if not room:
            return "Room not found", 404

        enc_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{token}.enc")
        if not os.path.exists(enc_path):
            return "File not found", 404

        with open(enc_path, 'rb') as fh:
            encrypted = fh.read()

        key = room.encryption_key
        f = Fernet(key.encode() if isinstance(key, str) else key)
        try:
            decrypted = f.decrypt(encrypted)
        except Exception as e:
            print('Decrypt error:', e)
            return 'Decrypt error', 500

        mime = msg.message_mime or 'application/octet-stream'
        return app.response_class(decrypted, mimetype=mime)
    except Exception as e:
        print('Media error:', e)
        return 'Server error', 500

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    return render_template('error.html', message='Halaman tidak ditemukan'), 404

@app.errorhandler(500)
def server_error(error):
    db.session.rollback()
    return render_template('error.html', message='Terjadi kesalahan server'), 500

# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)