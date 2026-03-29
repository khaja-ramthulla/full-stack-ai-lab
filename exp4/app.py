from flask import Flask, request, jsonify, render_template
import pickle
import numpy as np

app = Flask(__name__)

# Load models at startup
print("Loading models...")
with open('iris_logistic_regression.pkl', 'rb') as f:
    model = pickle.load(f)

with open('feature_names.pkl', 'rb') as f:
    feature_names = pickle.load(f)

with open('target_names.pkl', 'rb') as f:
    target_names = pickle.load(f)

print("Models loaded successfully!")

@app.route('/')
def home():
    return render_template(
        'index.html',
        feature_names=feature_names,
        target_names=target_names
    )

@app.route('/api/info', methods=['GET'])
def get_info():
    return jsonify({
        "description": "Iris Flower Classification API",
        "features": feature_names,
        "target_classes": list(target_names)
    })

@app.route('/api/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()

        if not data or 'features' not in data:
            return jsonify({"error": "Features are required"}), 400

        features = data['features']

        if len(features) != 4:
            return jsonify({"error": "Expected 4 input features"}), 400

        features_array = np.array([features])

        prediction = model.predict(features_array)
        pred_index = int(prediction[0])
        pred_class = target_names[pred_index]

        response = {
            "prediction": pred_class,
            "prediction_index": pred_index,
            "input_features": {
                feature_names[i]: features[i]
                for i in range(4)
            }
        }

        if hasattr(model, "predict_proba"):
            probs = model.predict_proba(features_array)[0]
            response["probabilities"] = {
                target_names[i]: float(probs[i])
                for i in range(len(target_names))
            }

        return jsonify(response)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
