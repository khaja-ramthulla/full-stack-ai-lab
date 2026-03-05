from flask import Flask, render_template, request, jsonify, session
from pymongo import MongoClient
import pickle, os
from dotenv import load_dotenv
from datetime import datetime
import bcrypt

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

# MongoDB connection
client = MongoClient(os.getenv('MONGO_URI'))
db = client['fullstack_ai_lab']
users_collection = db['users']
predictions_collection = db['spam_predictions']

# Load model
with open('models/spam_detector.pkl', 'rb') as f:
    spam_detector = pickle.load(f)
print("Spam detector model loaded successfully!")

# Decorator to require login
def require_login(f):
    def wrapper(*args, **kwargs):
        if 'user' not in session:
            return jsonify({'error': 'Not authenticated'}), 401
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        if not email or not password:
            return jsonify({'error': 'Email and password required'}), 400
        if users_collection.find_one({'email': email}):
            return jsonify({'error': 'Email already exists'}), 400
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        users_collection.insert_one({'email': email, 'password': hashed})
        return jsonify({'message': 'Registration successful'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        user = users_collection.find_one({'email': email})
        if not user or not bcrypt.checkpw(password.encode('utf-8'), user['password']):
            return jsonify({'error': 'Invalid credentials'}), 401
        session['user'] = email
        return jsonify({'message': 'Login successful', 'user': email}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/logout', methods=['POST'])
def logout():
    session.pop('user', None)
    return jsonify({'message': 'Logged out'}), 200

@app.route('/api/check-auth', methods=['GET'])
def check_auth():
    if 'user' in session:
        return jsonify({'authenticated': True, 'user': session['user']}), 200
    return jsonify({'authenticated': False}), 200

@app.route('/api/detect-spam', methods=['POST'])
@require_login
def detect_spam():
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        if not message or len(message) < 3:
            return jsonify({'error': 'Message required or too short'}), 400

        prediction = spam_detector.predict([message])[0]
        probabilities = spam_detector.predict_proba([message])[0]
        label = 'SPAM' if prediction==1 else 'HAM'
        spam_confidence = float(probabilities[1])
        ham_confidence = float(probabilities[0])

        # Store prediction
        record = {
            'user': session['user'],
            'timestamp': datetime.utcnow(),
            'message': message,
            'prediction': label,
            'spam_confidence': spam_confidence,
            'ham_confidence': ham_confidence,
            'message_length': len(message),
            'word_count': len(message.split())
        }
        result = predictions_collection.insert_one(record)

        return jsonify({
            'prediction': label,
            'spam_confidence': spam_confidence,
            'ham_confidence': ham_confidence,
            'record_id': str(result.inserted_id)
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/history', methods=['GET'])
@require_login
def history():
    try:
        user = session['user']
        limit = int(request.args.get('limit', 20))
        predictions = list(predictions_collection.find({'user': user}).sort('timestamp', -1).limit(limit))
        for pred in predictions:
            pred['_id'] = str(pred['_id'])
            pred['timestamp'] = pred['timestamp'].isoformat()
        return jsonify(predictions), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats', methods=['GET'])
@require_login
def stats():
    try:
        user = session['user']
        predictions = list(predictions_collection.find({'user': user}))
        total = len(predictions)
        spam_count = sum(1 for p in predictions if p['prediction']=='SPAM')
        ham_count = total - spam_count
        avg_spam_conf = sum(p['spam_confidence'] for p in predictions)/total if total>0 else 0
        avg_msg_len = sum(p['message_length'] for p in predictions)/total if total>0 else 0
        return jsonify({
            'total_messages': total,
            'spam_count': spam_count,
            'ham_count': ham_count,
            'spam_percentage': (spam_count/total*100) if total>0 else 0,
            'avg_spam_confidence': avg_spam_conf,
            'avg_message_length': avg_msg_len
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)