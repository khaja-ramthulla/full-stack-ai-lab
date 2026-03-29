from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from PIL import Image
from dotenv import load_dotenv
import numpy as np
from tensorflow.keras.models import load_model

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# MongoDB setup
mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
db = client["ai_lab"]
history = db["prediction_history"]

# Load ML model
model = load_model("mnist_cnn.h5")

def preprocess_image(path):
    img = Image.open(path).convert('L')

    w, h = img.size
    sz = max(w, h)
    padded = Image.new('L', (sz, sz), color=255)
    padded.paste(img, ((sz - w) // 2, (sz - h) // 2))

    small = padded.resize((28, 28), Image.LANCZOS)
    arr = np.array(small).astype(np.float32)

    if arr.mean() > 127:
        arr = 255.0 - arr

    arr = arr / 255.0
    arr = arr.reshape(1, 28, 28, 1)
    return arr

@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return jsonify(error="No file uploaded"), 400

    f = request.files['file']
    filename = secure_filename(f.filename)
    path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    f.save(path)

    X = preprocess_image(path)
    probs = model.predict(X)[0]
    pred = int(np.argmax(probs))
    conf = float(np.max(probs))

    history.insert_one({
        "filename": filename,
        "prediction": pred,
        "confidence": conf,
        "timestamp": datetime.now()
    })

    return jsonify(prediction=pred, confidence=conf, filename=filename)

@app.route('/api/history')
def api_history():
    docs = list(history.find().sort('timestamp', -1).limit(30))
    for d in docs:
        d['_id'] = str(d['_id'])
        d['timestamp'] = d['timestamp'].strftime('%Y-%m-%d %H:%M')
    return jsonify(docs)

if __name__ == '__main__':
    app.run(debug=True)
