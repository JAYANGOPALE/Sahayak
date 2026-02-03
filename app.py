import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError, OperationalError
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
app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql+psycopg2://{DB_USER}:{encoded_pass}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
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
    provider_id = db.Column(db.Integer, db.ForeignKey('providers.id'))
    service_type = db.Column(db.String, nullable=False)
    date = db.Column(db.String, nullable=False)
    time = db.Column(db.String, nullable=False)
    status = db.Column(db.String, default='Pending')
    cost = db.Column(db.Float, default=0.0)

    # Relationship to User (allows accessing service.user.address)
    user = db.relationship('User', backref='requests')
    provider = db.relationship('Provider', backref='requests')

class Transaction(db.Model):
    __tablename__ = 'transactions'
    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey('service_request.id'), nullable=False)
    provider_id = db.Column(db.Integer, db.ForeignKey('providers.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String, default='Pending')
    transaction_id = db.Column(db.String)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    service = db.relationship('ServiceRequest', backref='transactions')
    provider = db.relationship('Provider', backref='transactions')

# --- Routes ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        try:
            user = User.query.filter_by(username=username, password=password).first()
            if user:
                session['username'] = user.username
                return redirect(url_for('user_profile'))
            else:
                flash('Invalid credentials. Please try again.', 'error')
                return redirect(url_for('login'))
        except OperationalError:
            flash('Login credentials wrong. Please try again.', 'error')
            return redirect(url_for('login'))
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
        except OperationalError as e:
            db.session.rollback()
            return render_template('error.html', error_message=str(e))
            
    return render_template('signup.html')

@app.route('/user')
def user_profile():
    if 'username' in session:
        username = session['username']
        
        try:
            user = User.query.filter_by(username=username).first()
            history = ServiceRequest.query.filter_by(username=username).order_by(ServiceRequest.id.desc()).all()
        except OperationalError:
            flash('A database error occurred. Please try again later.', 'error')
            return redirect(url_for('user_profile'))
        
        # Check for unpaid services and redirect if necessary
        for service in history:
            if service.status == 'ACCEPTED_UNPAID':
                return redirect(url_for('payment', service_id=service.id))
                
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
        try:
            db.session.add(new_request)
            db.session.commit()
        except OperationalError as e:
            db.session.rollback()
            return render_template('error.html', error_message=str(e))
        
        return redirect(url_for('user_profile'))

    service = request.args.get('service')
    username = session.get('username')
    
    try:
        user = User.query.filter_by(username=username).first()
    except OperationalError as e:
        return render_template('error.html', error_message=str(e))
    return render_template('result.html', service=service, address=user.address if user else '')

# --- Provider Routes ---

@app.route('/provider/login', methods=['GET', 'POST'])
def provider_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        try:
            provider = Provider.query.filter_by(username=username, password=password).first()
            if provider:
                session['provider_username'] = provider.username
                return redirect(url_for('provider_dashboard'))
            else:
                flash('Invalid credentials. Please try again.', 'error')
                return redirect(url_for('provider_login'))
        except OperationalError:
            flash('Login credentials wrong. Please try again.', 'error')
            return redirect(url_for('provider_login'))
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
        except OperationalError as e:
            db.session.rollback()
            return render_template('error.html', error_message=str(e))
            
    return render_template('provider_signup.html')

@app.route('/provider/dashboard')
def provider_dashboard():
    if 'provider_username' not in session:
        return redirect(url_for('provider_login'))
    
    username = session['provider_username']
    
    try:
        provider = Provider.query.filter_by(username=username).first()
    except OperationalError as e:
        return render_template('error.html', error_message=str(e))
    
    if not provider:
        return redirect(url_for('provider_login'))
        
    provider_service_type = provider.service_type
    provider_address = provider.address.lower()
    
    # Find matching services
    # ORM makes this easier. We can fetch pending services of the type, 
    # and because of the relationship, we can check the user's address.
    
    try:
        potential_jobs = ServiceRequest.query.filter_by(
            service_type=provider_service_type, 
            status='Pending'
        ).all()
    except OperationalError as e:
        return render_template('error.html', error_message=str(e))
    
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

    provider_username = session['provider_username']
    
    try:
        provider = Provider.query.filter_by(username=provider_username).first()
        job = ServiceRequest.query.get(service_id)
    except OperationalError as e:
        return render_template('error.html', error_message=str(e))

    if job and provider:
        job.status = 'ACCEPTED_UNPAID'
        job.provider_id = provider.id
        job.cost = 500.00  # Hardcoded cost for now
        
        # Create a new transaction
        new_transaction = Transaction(
            service_id=job.id,
            provider_id=provider.id,
            amount=job.cost,
            status='Pending'
        )
        try:
            db.session.add(new_transaction)
            db.session.commit()
        except OperationalError as e:
            db.session.rollback()
            return render_template('error.html', error_message=str(e))
        
    return redirect(url_for('provider_dashboard'))

@app.route('/provider/reject/<int:service_id>')
def reject_service(service_id):
    if 'provider_username' not in session:
        return redirect(url_for('provider_login'))
        
    try:
        job = ServiceRequest.query.get(service_id)
    except OperationalError as e:
        return render_template('error.html', error_message=str(e))
    
    if job:
        job.status = 'Rejected'
        try:
            db.session.commit()
        except OperationalError as e:
            db.session.rollback()
            return render_template('error.html', error_message=str(e))
        
    return redirect(url_for('provider_dashboard'))

# --- Payment Routes ---

@app.route('/payment/<int:service_id>')
def payment(service_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    try:
        service = ServiceRequest.query.get(service_id)
    except OperationalError as e:
        return render_template('error.html', error_message=str(e))
    
    if not service or service.username != session['username']:
        return "Service not found or not authorized", 404

    return render_template('payment.html', service=service)

@app.route('/payment/success/<int:service_id>')
def payment_success(service_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    try:
        service = ServiceRequest.query.get(service_id)
        transaction = Transaction.query.filter_by(service_id=service_id).first()
    except OperationalError:
        flash('A database error occurred during payment confirmation. Please contact support.', 'error')
        return redirect(url_for('user_profile'))

    if service and transaction:
        service.status = 'PAYMENT_SUCCESS'
        transaction.status = 'Success'
        transaction.transaction_id = 'DUMMY_TRANSACTION_ID_12345'
        try:
            db.session.commit()
        except OperationalError as e:
            db.session.rollback()
            return render_template('error.html', error_message=str(e))

    return redirect(url_for('user_profile'))

@app.route('/payment/failed/<int:service_id>')
def payment_failed(service_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    try:
        service = ServiceRequest.query.get(service_id)
        transaction = Transaction.query.filter_by(service_id=service_id).first()
    except OperationalError:
        flash('A database error occurred during payment failure processing. Please contact support.', 'error')
        return redirect(url_for('user_profile'))

    if service and transaction:
        service.status = 'PAYMENT_FAILED'
        transaction.status = 'Failed'
        try:
            db.session.commit()
        except OperationalError as e:
            db.session.rollback()
            return render_template('error.html', error_message=str(e))

    return redirect(url_for('user_profile'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('provider_username', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    # with app.app_context():
    #     db.create_all()
    app.run(host='0.0.0.0', debug=True)
