
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
                time TEXT NOT NULL,
                status TEXT DEFAULT 'Pending'
            )
        ''')
        # Try to add status column if it doesn't exist (for existing DBs)
        try:
            cursor.execute('ALTER TABLE services ADD COLUMN status TEXT DEFAULT "Pending"')
        except sqlite3.OperationalError:
            pass # Column likely already exists

    with sqlite3.connect('providers.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS providers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                service_type TEXT NOT NULL,
                address TEXT,
                phone TEXT,
                email TEXT
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
        with sqlite3.connect('service.db') as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM services WHERE username = ?', (username,))
            service_history = cursor.fetchall()
        return render_template('user.html', user=user_data, history=service_history)
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
            cursor.execute('INSERT INTO services (username, service_type, date, time, status) VALUES (?, ?, ?, ?, ?)',
                           (username, service_type, date, time, 'Pending'))
            conn.commit()
        return redirect(url_for('user_profile'))

    service = request.args.get('service')
    username = session.get('username')
    with sqlite3.connect('user.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT address FROM users WHERE username = ?', (username,))
        address = cursor.fetchone()
    return render_template('result.html', service=service, address=address[0] if address else '')

# --- Provider Routes ---

@app.route('/provider/login', methods=['GET', 'POST'])
def provider_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        with sqlite3.connect('providers.db') as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM providers WHERE username = ? AND password = ?', (username, password))
            provider = cursor.fetchone()
            if provider:
                session['provider_username'] = provider[1]
                return redirect(url_for('provider_dashboard'))
            else:
                return 'Invalid credentials'
    return render_template('provider_login.html')

@app.route('/provider/signup', methods=['GET', 'POST'])
def provider_signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        phone = request.form['phone']
        address = request.form['address']
        service_type = request.form['service_type']
        
        with sqlite3.connect('providers.db') as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('INSERT INTO providers (username, password, service_type, address, phone, email) VALUES (?, ?, ?, ?, ?, ?)',
                               (username, password, service_type, address, phone, email))
                conn.commit()
            except sqlite3.IntegrityError:
                return 'Username already exists'
        session['provider_username'] = username
        return redirect(url_for('provider_dashboard'))
    return render_template('provider_signup.html')

@app.route('/provider/dashboard')
def provider_dashboard():
    if 'provider_username' not in session:
        return redirect(url_for('provider_login'))
    
    username = session['provider_username']
    
    # Get provider details
    with sqlite3.connect('providers.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM providers WHERE username = ?', (username,))
        provider = cursor.fetchone()
        
    if not provider:
        return redirect(url_for('provider_login'))
        
    provider_service_type = provider[3]
    provider_address = provider[4].lower() # Simple string match
    
    # Find matching services
    # We need to cross-reference service requests with user addresses
    available_jobs = []
    
    with sqlite3.connect('service.db') as conn:
        cursor = conn.cursor()
        # Fetch all pending services of the matching type
        cursor.execute('SELECT * FROM services WHERE service_type = ? AND status = "Pending"', (provider_service_type,))
        services = cursor.fetchall()
        
    # Now filter by location (requires looking up user address)
    with sqlite3.connect('user.db') as conn:
        user_cursor = conn.cursor()
        for service in services:
            client_username = service[1]
            user_cursor.execute('SELECT address, phone, email FROM users WHERE username = ?', (client_username,))
            user_info = user_cursor.fetchone()
            
            if user_info:
                user_address = user_info[0].lower()
                # Basic check: if provider's city/area is in user's address
                if provider_address in user_address or user_address in provider_address:
                    # Add to list: (service_id, client_name, date, time, address, phone)
                    available_jobs.append({
                        'id': service[0],
                        'client': client_username,
                        'date': service[3],
                        'time': service[4],
                        'address': user_info[0],
                        'phone': user_info[1]
                    })
                    
    return render_template('provider_dashboard.html', provider=provider, jobs=available_jobs)

@app.route('/provider/accept/<int:service_id>')
def accept_service(service_id):
    if 'provider_username' not in session:
        return redirect(url_for('provider_login'))
        
    with sqlite3.connect('service.db') as conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE services SET status = "Accepted" WHERE id = ?', (service_id,))
        conn.commit()
        
    return redirect(url_for('provider_dashboard'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('provider_username', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', debug=True)
