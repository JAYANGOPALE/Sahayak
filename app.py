import os
from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from dotenv import load_dotenv
from urllib.parse import quote_plus

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'default_secret_key')

# --- Supabase / PostgreSQL Configuration (SQLAlchemy) ---
DB_HOST = os.getenv('DB_HOST')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PORT = os.getenv('DB_PORT')
DB_PASS = os.getenv('DB_PASS')

# Construct Database URI with URL-encoded password
encoded_pass = quote_plus(DB_PASS) if DB_PASS else ""
app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{DB_USER}:{encoded_pass}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- Models ---

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    address = db.Column(db.String)
    phone = db.Column(db.String)
    email = db.Column(db.String)

class Provider(db.Model):
    __tablename__ = 'providers'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    service_type = db.Column(db.String, nullable=False)
    address = db.Column(db.String)
    phone = db.Column(db.String)
    email = db.Column(db.String)

class ServiceRequest(db.Model):
    __tablename__ = 'service_request' # Renamed from 'services'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, db.ForeignKey('users.username'), nullable=False)
    service_type = db.Column(db.String, nullable=False)
    date = db.Column(db.String, nullable=False)
    time = db.Column(db.String, nullable=False)
    status = db.Column(db.String, default='Pending')

    # Relationship to User (allows accessing service.user.address)
    user = db.relationship('User', backref='requests')

# --- Routes ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username, password=password).first()
        
        if user:
            session['username'] = user.username
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
        
        new_user = User(username=username, password=password, email=email, phone=phone, address=address)
        
        try:
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect(url_for('user_profile'))
        except IntegrityError:
            db.session.rollback()
            return 'Username already exists'
            
    return render_template('signup.html')

@app.route('/user')
def user_profile():
    if 'username' in session:
        username = session['username']
        
        user = User.query.filter_by(username=username).first()
        # Fetch Service History (ordered by id desc for latest first, optional but nice)
        history = ServiceRequest.query.filter_by(username=username).order_by(ServiceRequest.id.desc()).all()
        
        # We need to pass data in a format the template expects (tuples or objects).
        # The template currently expects tuples: item[2], item[3] etc.
        # But with ORM we pass objects: item.service_type, item.date.
        # **TEMPLATE CHANGE REQUIRED** or we simulate tuples? 
        # Better to update the Template to use object attributes.
        # For now, I will let the user know, OR I can modify the template.
        # Actually, let's pass the objects and I will update the template in the next step.
        
        return render_template('user.html', user=user, history=history)
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
        
        new_request = ServiceRequest(
            username=username,
            service_type=service_type,
            date=date,
            time=time,
            status='Pending'
        )
        db.session.add(new_request)
        db.session.commit()
        
        return redirect(url_for('user_profile'))

    service = request.args.get('service')
    username = session.get('username')
    
    user = User.query.filter_by(username=username).first()
    return render_template('result.html', service=service, address=user.address if user else '')

# --- Provider Routes ---

@app.route('/provider/login', methods=['GET', 'POST'])
def provider_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        provider = Provider.query.filter_by(username=username, password=password).first()
        
        if provider:
            session['provider_username'] = provider.username
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
        
        new_provider = Provider(
            username=username,
            password=password,
            email=email,
            phone=phone,
            address=address,
            service_type=service_type
        )
        
        try:
            db.session.add(new_provider)
            db.session.commit()
            session['provider_username'] = username
            return redirect(url_for('provider_dashboard'))
        except IntegrityError:
            db.session.rollback()
            return 'Username already exists'
            
    return render_template('provider_signup.html')

@app.route('/provider/dashboard')
def provider_dashboard():
    if 'provider_username' not in session:
        return redirect(url_for('provider_login'))
    
    username = session['provider_username']
    
    provider = Provider.query.filter_by(username=username).first()
    
    if not provider:
        return redirect(url_for('provider_login'))
        
    provider_service_type = provider.service_type
    provider_address = provider.address.lower()
    
    # Find matching services
    # ORM makes this easier. We can fetch pending services of the type, 
    # and because of the relationship, we can check the user's address.
    
    potential_jobs = ServiceRequest.query.filter_by(
        service_type=provider_service_type, 
        status='Pending'
    ).all()
    
    available_jobs = []
    
    for job in potential_jobs:
        # Access the related User object directly
        if job.user:
            user_address = job.user.address.lower()
            if provider_address in user_address or user_address in provider_address:
                available_jobs.append({
                    'id': job.id,
                    'client': job.username,
                    'date': job.date,
                    'time': job.time,
                    'address': job.user.address,
                    'phone': job.user.phone
                })
                    
    return render_template('provider_dashboard.html', provider=provider, jobs=available_jobs)

@app.route('/provider/accept/<int:service_id>')
def accept_service(service_id):
    if 'provider_username' not in session:
        return redirect(url_for('provider_login'))
        
    job = ServiceRequest.query.get(service_id)
    if job:
        job.status = 'Accepted'
        db.session.commit()
        
    return redirect(url_for('provider_dashboard'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('provider_username', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', debug=True)