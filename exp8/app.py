from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
from PIL import Image
import numpy as np
import os
from tensorflow.keras.models import load_model

app = Flask(__name__)

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

model = load_model("mnist_cnn.h5")

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def preprocess_image(path):
    img = Image.open(path).convert('L')
    w, h = img.size
    size = max(w, h)

    padded = Image.new('L', (size, size), color=255)
    padded.paste(img, ((size - w) // 2, (size - h) // 2))

    img = padded.resize((28, 28))
    arr = np.array(img).astype(np.float32)

    if arr.mean() > 127:
        arr = 255 - arr

    arr = arr / 255.0
    arr = arr.reshape(1, 28, 28, 1)
    return arr

@app.route('/')
def index():
    return render_template('upload.html')

@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return jsonify(error="No file uploaded"), 400

    file = request.files['file']

    if file.filename == '' or not allowed_file(file.filename):
        return jsonify(error="Invalid file type"), 400

    filename = secure_filename(file.filename)
    path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(path)

    X = preprocess_image(path)
    probs = model.predict(X)[0]

    prediction = int(np.argmax(probs))
    confidence = float(np.max(probs))

    return jsonify(
        prediction=prediction,
        confidence=confidence,
        filename=filename
    )

if __name__ == '__main__':
    app.run(debug=True)
