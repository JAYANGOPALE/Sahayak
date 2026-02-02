import os
import psycopg2
from psycopg2 import IntegrityError
from flask import Flask, render_template, request, redirect, url_for, session
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'default_secret_key')

# --- Supabase / PostgreSQL Configuration ---
DB_HOST = os.getenv('DB_HOST')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PORT = os.getenv('DB_PORT')
DB_PASS = os.getenv('DB_PASS')

def get_db_connection():
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        port=DB_PORT
    )
    return conn

# --- Database Initialization ---
def init_db():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Create Users Table
        cur.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                address TEXT,
                phone TEXT,
                email TEXT
            )
        ''')
        
        # Create Services Table
        cur.execute('''
            CREATE TABLE IF NOT EXISTS services (
                id SERIAL PRIMARY KEY,
                username TEXT NOT NULL,
                service_type TEXT NOT NULL,
                date TEXT NOT NULL,
                time TEXT NOT NULL,
                status TEXT DEFAULT 'Pending'
            )
        ''')

        # Create Providers Table
        cur.execute('''
            CREATE TABLE IF NOT EXISTS providers (
                id SERIAL PRIMARY KEY,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                service_type TEXT NOT NULL,
                address TEXT,
                phone TEXT,
                email TEXT
            )
        ''')
        
        conn.commit()
        cur.close()
        conn.close()
        print("Database initialized successfully.")
    except Exception as e:
        print(f"Error initializing database: {e}")

@app.route('/')
def index():
    return render_template('index.html')

# --- User Routes ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        cur = conn.cursor()
        # Note: Postgres uses %s for placeholders, not ?
        cur.execute('SELECT * FROM users WHERE username = %s AND password = %s', (username, password))
        user = cur.fetchone()
        cur.close()
        conn.close()
        
        if user:
            session['username'] = user[1] # username is at index 1
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
        
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute('INSERT INTO users (username, password, email, phone, address) VALUES (%s, %s, %s, %s, %s)',
                           (username, password, email, phone, address))
            conn.commit()
        except IntegrityError:
            conn.rollback()
            return 'Username already exists'
        finally:
            cur.close()
            conn.close()
            
        session['username'] = username
        return redirect(url_for('user_profile'))
    return render_template('signup.html')

@app.route('/user')
def user_profile():
    if 'username' in session:
        username = session['username']
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Fetch User Data
        cur.execute('SELECT * FROM users WHERE username = %s', (username,))
        user_data = cur.fetchone()
        
        # Fetch Service History
        cur.execute('SELECT * FROM services WHERE username = %s', (username,))
        service_history = cur.fetchall()
        
        cur.close()
        conn.close()
        
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
        
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('INSERT INTO services (username, service_type, date, time, status) VALUES (%s, %s, %s, %s, %s)',
                       (username, service_type, date, time, 'Pending'))
        conn.commit()
        cur.close()
        conn.close()
        
        return redirect(url_for('user_profile'))

    service = request.args.get('service')
    username = session.get('username')
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT address FROM users WHERE username = %s', (username,))
    address_row = cur.fetchone()
    cur.close()
    conn.close()
    
    return render_template('result.html', service=service, address=address_row[0] if address_row else '')

# --- Provider Routes ---

@app.route('/provider/login', methods=['GET', 'POST'])
def provider_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM providers WHERE username = %s AND password = %s', (username, password))
        provider = cur.fetchone()
        cur.close()
        conn.close()
        
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
        
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute('INSERT INTO providers (username, password, service_type, address, phone, email) VALUES (%s, %s, %s, %s, %s, %s)',
                           (username, password, service_type, address, phone, email))
            conn.commit()
        except IntegrityError:
            conn.rollback()
            return 'Username already exists'
        finally:
            cur.close()
            conn.close()
            
        session['provider_username'] = username
        return redirect(url_for('provider_dashboard'))
    return render_template('provider_signup.html')

@app.route('/provider/dashboard')
def provider_dashboard():
    if 'provider_username' not in session:
        return redirect(url_for('provider_login'))
    
    username = session['provider_username']
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Get provider details
    cur.execute('SELECT * FROM providers WHERE username = %s', (username,))
    provider = cur.fetchone()
    
    if not provider:
        cur.close()
        conn.close()
        return redirect(url_for('provider_login'))
        
    provider_service_type = provider[3]
    provider_address = provider[4].lower()
    
    # Find matching services
    # Ideally, we would do a JOIN in SQL, but keeping logic similar to before for now
    available_jobs = []
    
    # Fetch all pending services of the matching type
    cur.execute('SELECT * FROM services WHERE service_type = %s AND status = %s', (provider_service_type, 'Pending'))
    services = cur.fetchall()
    
    for service in services:
        client_username = service[1]
        # Fetch user details for this service
        # Using a separate cursor execution inside the loop (not efficient for huge data, but fine for now)
        cur.execute('SELECT address, phone, email FROM users WHERE username = %s', (client_username,))
        user_info = cur.fetchone()
        
        if user_info:
            user_address = user_info[0].lower()
            if provider_address in user_address or user_address in provider_address:
                available_jobs.append({
                    'id': service[0],
                    'client': client_username,
                    'date': service[3],
                    'time': service[4],
                    'address': user_info[0],
                    'phone': user_info[1]
                })
    
    cur.close()
    conn.close()
                    
    return render_template('provider_dashboard.html', provider=provider, jobs=available_jobs)

@app.route('/provider/accept/<int:service_id>')
def accept_service(service_id):
    if 'provider_username' not in session:
        return redirect(url_for('provider_login'))
        
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('UPDATE services SET status = %s WHERE id = %s', ('Accepted', service_id))
    conn.commit()
    cur.close()
    conn.close()
        
    return redirect(url_for('provider_dashboard'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('provider_username', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    # Initialize DB (Create tables if they don't exist)
    init_db()
    # Host 0.0.0.0 is still useful if you want to test on local LAN before deploying
    app.run(host='0.0.0.0', debug=True)