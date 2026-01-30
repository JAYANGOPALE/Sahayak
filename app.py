
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a real secret key

# Database initialization
def init_db():
    with sqlite3.connect('user.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                address TEXT,
                phone TEXT,
                email TEXT
            )
        ''')
    with sqlite3.connect('service.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS services (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                service_type TEXT NOT NULL,
                date TEXT NOT NULL,
                time TEXT NOT NULL
            )
        ''')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        with sqlite3.connect('user.db') as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
            user = cursor.fetchone()
            if user:
                session['username'] = user[1]
                return redirect(url_for('user_profile'))
            else:
                return 'Invalid credentials'
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        phone = request.form['phone']
        address = request.form['address']
        with sqlite3.connect('user.db') as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('INSERT INTO users (username, password, email, phone, address) VALUES (?, ?, ?, ?, ?)',
                               (username, password, email, phone, address))
                conn.commit()
            except sqlite3.IntegrityError:
                return 'Username already exists'
        session['username'] = username
        return redirect(url_for('user_profile'))
    return render_template('signup.html')

@app.route('/user')
def user_profile():
    if 'username' in session:
        username = session['username']
        with sqlite3.connect('user.db') as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
            user_data = cursor.fetchone()
        return render_template('user.html', user=user_data)
    return redirect(url_for('login'))

@app.route('/result', methods=['GET', 'POST'])
def result():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        service_type = request.form['service_type']
        date = request.form['date']
        time = request.form['time']
        username = session['username']
        
        with sqlite3.connect('service.db') as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO services (username, service_type, date, time) VALUES (?, ?, ?, ?)',
                           (username, service_type, date, time))
            conn.commit()
        return redirect(url_for('user_profile'))

    service = request.args.get('service')
    username = session.get('username')
    with sqlite3.connect('user.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT address FROM users WHERE username = ?', (username,))
        address = cursor.fetchone()
    return render_template('result.html', service=service, address=address[0] if address else '')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
