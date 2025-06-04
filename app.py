from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import sqlite3
from flask import abort

API_TOKEN = "token123"

app = Flask(__name__)
CORS(app)

def check_auth():
    token = request.headers.get('Authorization')
    if token != f"Bearer {API_TOKEN}":
        abort(401)

def init_db():
    conn = sqlite3.connect('messages.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/contact', methods=['POST'])
def contact():
    data = request.json
    name = data.get('name')
    email = data.get('email')
    message = data.get('message')
    conn = sqlite3.connect('messages.db')
    c = conn.cursor()
    c.execute("INSERT INTO messages (name, email, message) VALUES (?, ?, ?)",
              (name, email, message))
    conn.commit()
    conn.close()
    print(f"Nowa wiadomość od {name} ({email}): {message}")

    return jsonify({'status': 'success', 'message': 'Dziękujemy za kontakt!'})

@app.route('/messages', methods=['GET'])
def get_messages():
    check_auth()
    
    conn = sqlite3.connect('messages.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM messages ORDER BY created_at DESC")
    rows = c.fetchall()
    conn.close()

    messages = []
    for row in rows:
        messages.append({
            'id': row['id'],
            'name': row['name'],
            'email': row['email'],
            'message': row['message'],
            'created_at': row['created_at']
        })

    return jsonify(messages)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
