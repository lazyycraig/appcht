# 🔐 Dokumentasi Teknis - Chat Terenkripsi

## Arsitektur Sistem

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (Browser)                        │
│  HTML + CSS + JavaScript + Socket.IO Client                 │
└──────────────────────┬──────────────────────────────────────┘
                       │ WebSocket (Real-time)
                       │ HTTPS (Secure)
┌──────────────────────▼──────────────────────────────────────┐
│                    Backend (Flask)                           │
│  ├─ REST API Routes (HTTP)                                  │
│  ├─ WebSocket Handler (Socket.IO)                           │
│  ├─ Encryption/Decryption Layer                             │
│  └─ Database ORM (SQLAlchemy)                               │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                  SQLite Database                             │
│  ├─ ChatRooms (Terenkripsi)                                 │
│  ├─ Messages (Terenkripsi)                                  │
│  └─ Sessions (Aman)                                         │
└─────────────────────────────────────────────────────────────┘
```

---

## Data Flow

### 1. Create Chat Room

```
User Browser
     │
     ├─ POST /create-room
     │  ├─ Generate room_id (token_hex)
     │  ├─ Generate access_link (token_urlsafe)
     │  ├─ Generate encryption_key (Fernet.generate_key())
     │  └─ Save to database
     │
     └─ Return room details + QR code
```

### 2. Join Chat Room

```
User Browser (via link)
     │
     ├─ GET /join/<access_link>
     │  ├─ Query database by access_link
     │  ├─ Validate room exists
     │  └─ Check if room not full (max 2 users)
     │
     ├─ POST /join-room
     │  ├─ Update room dengan user2_id dan user2_name
     │  └─ Create user session
     │
     └─ Redirect to /chat/<room_id>
```

### 3. Send Message

```
User A
  │
  ├─ Type message in UI
  │
  ├─ Emit 'send_message' event (WebSocket)
  │  ├─ Include: room_id, user_id, user_name, content
  │  │
  │  └─ Backend receives:
  │     ├─ Encrypt message dengan room.encryption_key
  │     ├─ Save encrypted message ke database
  │     ├─ Emit 'new_message' dengan content (decrypted)
  │     │  └─ Send ke semua user di room
  │     │
  │     └─ User A dan B receive pesan
  │        └─ Display di UI dengan sender info
```

### 4. Online Status Indicator

```
WebSocket Connection Flow:

User Connect
     │
     ├─ Socket.on('connect')
     │  ├─ Add user_id to online_users dict
     │  └─ Emit 'user_status_changed' (online=true)
     │
User Disconnect
     │
     └─ Socket.on('disconnect')
        ├─ Remove user_id from online_users dict
        └─ Emit 'user_status_changed' (online=false)

Check Online Status (Real-time)
     │
     ├─ Client emit 'check_online' setiap 3 detik
     │
     └─ Server emit 'online_status' dengan:
        ├─ user1_online (boolean)
        └─ user2_online (boolean)
```

---

## Encryption Details

### Fernet (Symmetric Encryption)

```python
from cryptography.fernet import Fernet

# Generate key (dilakukan saat create room)
key = Fernet.generate_key()
# Output: b'...(44 characters base64)...'

# Create cipher
cipher = Fernet(key)

# Encrypt
plaintext = b"Hello, this is my message"
ciphertext = cipher.encrypt(plaintext)
# Output: b'gAAAAABj...(base64 encoded)...'

# Decrypt
decrypted = cipher.decrypt(ciphertext)
# Output: b"Hello, this is my message"
```

### Key Specifications

- **Algorithm**: AES-128 in CBC mode
- **IV**: Random per message (128-bit)
- **Hmac**: SHA256 untuk authentication
- **Key Length**: 256-bit (encoded dalam base64)
- **Encoding**: All stored as base64 strings

### Message Encryption Process

```
Plain Message (String)
     │
     ├─ Encode to UTF-8 bytes
     │
     ├─ Encrypt dengan Fernet key
     │  └─ AES-128-CBC + HMAC-SHA256
     │
     ├─ Base64 encode result
     │
     └─ Store di database sebagai string
        └─ Set is_encrypted = True


Message Retrieval & Decryption
     │
     ├─ Fetch dari database (still base64 encoded)
     │
     ├─ Fernet.decrypt() dengan room.encryption_key
     │  └─ Validate HMAC
     │  └─ AES-128-CBC decrypt
     │
     ├─ Decode dari UTF-8 bytes ke string
     │
     └─ Display di UI
```

---

## Database Schema

### Table: chat_rooms

```sql
CREATE TABLE chat_rooms (
    id VARCHAR(36) PRIMARY KEY,              -- Unique room ID
    access_link VARCHAR(255) UNIQUE NOT NULL,  -- Share link
    encryption_key VARCHAR(255) NOT NULL,   -- Fernet key (base64)
    user1_id VARCHAR(36),                   -- Creator ID
    user2_id VARCHAR(36),                   -- Joiner ID
    user1_name VARCHAR(100) NOT NULL,       -- Creator name
    user2_name VARCHAR(100),                -- Joiner name
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Table: messages

```sql
CREATE TABLE messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    room_id VARCHAR(36) NOT NULL,           -- FK to chat_rooms
    sender_id VARCHAR(36) NOT NULL,         -- Who sent it
    sender_name VARCHAR(100) NOT NULL,      -- Display name
    content TEXT NOT NULL,                  -- Encrypted message
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_encrypted BOOLEAN DEFAULT TRUE,      -- Encryption flag
    FOREIGN KEY (room_id) REFERENCES chat_rooms(id)
);
```

### Indexes

```sql
CREATE INDEX idx_access_link ON chat_rooms(access_link);
CREATE INDEX idx_room_id ON messages(room_id);
CREATE INDEX idx_timestamp ON messages(timestamp);
```

---

## API Endpoints Detail

### 1. GET /
**Purpose**: Home page
```
Response: HTML (index.html)
```

### 2. POST /create-room
**Purpose**: Create new chat room
```
Request:
{
    "name": "Alice"  (string, min 2 chars)
}

Response Success (200):
{
    "room_id": "a1b2c3d4",
    "access_link": "safe_random_token_32_chars",
    "status": "created"
}

Response Error (400/500):
{
    "error": "Error message"
}
```

### 3. GET /join/<link>
**Purpose**: Join page via link
```
URL Params:
- link: access_link token

Response:
- HTML (join.html) jika link valid
- Error page jika link invalid atau room full
```

### 4. POST /join-room
**Purpose**: Join existing room
```
Request:
{
    "name": "Bob",
    "access_link": "safe_random_token"
}

Response Success (200):
{
    "room_id": "a1b2c3d4",
    "status": "joined"
}

Response Error (400/404/500):
{
    "error": "Error message"
}
```

### 5. GET /chat/<room_id>
**Purpose**: Chat page
```
URL Params:
- room_id: room identifier

Returns:
- Chat page with message history (decrypted)
- Redirect to index if invalid session
```

### 6. GET /api/room-status/<room_id>
**Purpose**: Get room status
```
Response:
{
    "user1_online": boolean,
    "user1_name": "Alice",
    "user2_online": boolean,
    "user2_name": "Bob",
    "room_full": boolean
}
```

---

## WebSocket Events

### Client → Server

#### connect
```javascript
emit('connect', {
    user_id: "...",
    room_id: "...",
    user_name: "Alice"
})
// Backend: Add to online_users dict
```

#### send_message
```javascript
emit('send_message', {
    room_id: "...",
    user_id: "...",
    user_name: "Alice",
    content: "Hello Bob!"
})
// Backend: Encrypt, save, broadcast
```

#### check_online
```javascript
emit('check_online', {
    room_id: "...",
    user_id: "..."
})
// Backend: Return current online status
```

#### disconnect
```javascript
// Automatic when user disconnects
// Backend: Remove from online_users
```

### Server → Client

#### new_message
```javascript
on('new_message', (data) => {
    // data = {id, sender_name, sender_id, content, timestamp}
    // content sudah di-decrypt
})
```

#### user_status_changed
```javascript
on('user_status_changed', (data) => {
    // data = {user_id, user_name, online: boolean}
})
```

#### online_status
```javascript
on('online_status', (data) => {
    // data = {user1_online, user2_online}
})
```

#### error
```javascript
on('error', (data) => {
    // data = {message: "Error description"}
})
```

---

## Security Considerations

### ✅ Implemented

1. **Encryption**
   - Fernet symmetric encryption (AES-128)
   - Per-room unique key
   - HMAC for integrity

2. **Session Management**
   - Secure session cookies
   - HttpOnly flag
   - SameSite=Lax

3. **Access Control**
   - Random access link (32 chars)
   - Room capacity limit (max 2)
   - Link validation on join

4. **Input Validation**
   - Name min 2 chars
   - Message max 2000 chars
   - XSS prevention via escapeHtml()

### ⚠️ To Do for Production

1. **HTTPS/SSL**
   - Use SSL certificates
   - Redirect HTTP to HTTPS
   ```nginx
   server {
       listen 443 ssl;
       ssl_certificate /path/to/cert.pem;
       ssl_certificate_key /path/to/key.pem;
   }
   ```

2. **Rate Limiting**
   - Prevent message spam
   - Limit room creation per IP
   ```python
   from flask_limiter import Limiter
   limiter = Limiter(app, key_func=get_remote_address)
   ```

3. **CORS Protection**
   - Whitelist origins
   ```python
   CORS(app, origins=['https://yourdomain.com'])
   ```

4. **Database Hardening**
   - Use PostgreSQL for production
   - Add connection pooling
   - Enable query logging

5. **Logging & Monitoring**
   - Log all connections
   - Monitor encryption operations
   - Alert on suspicious activity

---

## Performance Optimization

### Current Limits
- Message size: 2000 chars
- Room capacity: 2 users
- Database: SQLite (OK untuk 1000s of messages)

### For Scalability

1. **Switch to PostgreSQL**
   ```bash
   pip install psycopg2-binary
   # Update DATABASE_URI
   ```

2. **Add Redis for Caching**
   ```bash
   pip install flask-redis
   # Cache online status
   ```

3. **Connection Pooling**
   ```python
   app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
       'pool_size': 10,
       'pool_recycle': 3600
   }
   ```

4. **Message Pagination**
   ```python
   @app.route('/api/messages/<room_id>?page=1&limit=50')
   def get_messages_paginated(room_id):
       page = request.args.get('page', 1, type=int)
       limit = request.args.get('limit', 50, type=int)
       # ...
   ```

---

## Deployment Checklist

- [ ] Update `SECRET_KEY` dengan random strong key
- [ ] Set `FLASK_ENV=production`
- [ ] Set `FLASK_DEBUG=False`
- [ ] Setup SSL certificates
- [ ] Configure Nginx reverse proxy
- [ ] Setup PostgreSQL database
- [ ] Enable logging & monitoring
- [ ] Setup backup mechanism
- [ ] Configure firewall rules
- [ ] Setup auto-restart (systemd/supervisor)

---

## Development Tips

### Local Testing

```bash
# Terminal 1: Run Flask
python app.py

# Terminal 2: Access logs
tail -f app.log

# Browser 1: Tab A (Create room)
localhost:5000

# Browser 2: Tab B (Join room)
localhost:5000/join/<access_link>
```

### Debug WebSocket

```javascript
// In browser console
socket.on('connect', () => console.log('Connected'));
socket.on('disconnect', () => console.log('Disconnected'));
socket.on('new_message', (data) => console.log('Message:', data));
```

### Inspect Database

```bash
# SQLite CLI
sqlite3 chat.db

# List tables
.tables

# Query messages
SELECT * FROM messages;

# Query rooms
SELECT * FROM chat_rooms;
```

---

## Future Enhancements

1. **Group Chat**
   - Extend to >2 users per room
   - Admin controls

2. **File Sharing**
   - Encrypted file upload
   - Size limits

3. **Voice/Video**
   - WebRTC integration
   - End-to-end encryption

4. **Message Features**
   - Reactions/Emojis
   - Delete messages
   - Edit messages

5. **User Profiles**
   - Avatar support
   - Status message
   - Last seen

---

**Last Updated: 2026-05-25**
