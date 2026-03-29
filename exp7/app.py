from flask import Flask, request, jsonify, render_template
from flask_jwt_extended import (
    JWTManager, create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity, get_jwt
)
from pymongo import MongoClient
import bcrypt
import os
from dotenv import load_dotenv
from datetime import timedelta, datetime

load_dotenv()

app = Flask(__name__)

# JWT configuration
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)

jwt = JWTManager(app)

# MongoDB
client = MongoClient(os.getenv('MONGO_URI'))
db = client['fullstack_ai_lab']
users = db['users']
revoked_tokens = db['revoked_tokens']


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'Email and password required'}), 400

    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400

    if users.find_one({'email': email}):
        return jsonify({'error': 'Email already registered'}), 400

    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    users.insert_one({
        'email': email,
        'password': hashed,
        'created_at': datetime.utcnow()
    })

    return jsonify({'message': 'User registered successfully'}), 201


@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = users.find_one({'email': email})
    if not user or not bcrypt.checkpw(password.encode(), user['password']):
        return jsonify({'error': 'Invalid credentials'}), 401

    return jsonify({
        'access_token': create_access_token(identity=email),
        'refresh_token': create_refresh_token(identity=email),
        'user': email
    })


@app.route('/api/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    return jsonify({
        'access_token': create_access_token(identity=get_jwt_identity())
    })


@app.route('/api/protected')
@jwt_required()
def protected():
    return jsonify({
        'message': 'Access granted',
        'user': get_jwt_identity(),
        'timestamp': datetime.utcnow().isoformat()
    })


@app.route('/api/logout', methods=['POST'])
@jwt_required()
def logout():
    revoked_tokens.insert_one({'jti': get_jwt()['jti']})
    return jsonify({'message': 'Logged out successfully'})


@jwt.token_in_blocklist_loader
def check_revoked(jwt_header, jwt_payload):
    return revoked_tokens.find_one({'jti': jwt_payload['jti']}) is not None


@jwt.expired_token_loader
def expired_callback(jwt_header, jwt_payload):
    return jsonify({'error': 'Token expired'}), 401


@jwt.unauthorized_loader
def missing_callback(error):
    return jsonify({'error': 'Authorization header required'}), 401


if __name__ == '__main__':
    app.run(debug=True)
