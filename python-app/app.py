from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from prometheus_client import Summary, Counter, Histogram, generate_latest
import time

import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://admin:admin5896@postgresql/flask_db'
db = SQLAlchemy(app)
with app.app_context():
    db.create_all()

# Start time of the application
start_time = time.time()

# Define the User model
class User(db.Model):
    __tablename__='users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

# Prometheus metrics (moved from the route to global scope)
total_requests = Counter('total_requests', 'Total number of requests')
login_requests = Counter('login_requests', 'Total number of login accesses')
request_duration = Histogram('request_duration_seconds', 'Duration of requests')
total_errors = Counter('total_errors', 'Total number of errors')
failed_login_attempts = Counter('failed_login_attempts', 'Failed login attempts')
successful_login_attempts = Counter('successful_login_attempts', 'Successful login attempts')
time_taken_successful_logins = Histogram('time_taken_successful_logins_seconds', 'Time taken for successful logins')
successful_requests = Counter('successful_requests', 'Total number of successful requests')

@app.route('/')
def home():
    total_requests.inc()
    return 'Welcome to the Flask Prometheus Monitoring Example!'

@app.route('/login', methods=['GET', 'POST'])
def login():
    login_requests.inc()
    start_time = time.time()

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        logger.info(f'password {password}')
        user = User.query.filter_by(username=username).first()
        if user:
            session['username'] = user.username
            logger.info(f'User {username} logged in successfully.')
            duration = time.time() - start_time
            time_taken_successful_logins.observe(duration)
            successful_login_attempts.inc()
            return redirect(url_for('dashboard'))
        else:
            logger.warning(f'Failed login attempt for username: {username}.')
            failed_login_attempts.inc()
            total_errors.inc()
            return render_template('login.html', error='Invalid username or password.')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/success_percentage')
def success_percentage():
    total = total_requests._sum_data.values()[0]
    success = successful_requests._sum_data.values()[0]
    percentage = (success / total) * 100 if total > 0 else 0
    return f"Percentage of 2xx requests: {percentage:.2f}%"

@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        return render_template('dashboard.html', username=session['username'])
    return redirect(url_for('login'))

@app.route('/metrics')
def metrics():
    return generate_latest()

@app.before_request
def before_request():
    request.start_time = time.time()

@app.after_request
def after_request(response):
    latency = time.time() - request.start_time
    request_duration.observe(latency)
    return response

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
