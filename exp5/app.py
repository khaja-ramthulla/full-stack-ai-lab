from flask import Flask, request, jsonify, render_template
import pickle
import numpy as np

app = Flask(__name__)

# Load trained model and metadata
with open('iris_logistic_regression.pkl', 'rb') as f:
    model = pickle.load(f)

with open('feature_names.pkl', 'rb') as f:
    feature_names = pickle.load(f)

with open('target_names.pkl', 'rb') as f:
    target_names = pickle.load(f)

@app.route('/')
def home():
    return render_template(
        'predict.html',
        feature_names=feature_names,
        target_names=target_names
    )

@app.route('/api/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        features = data.get('features')

        if not features or len(features) != 4:
            return jsonify({'error': 'Expected 4 input features'}), 400

        features_array = np.array([features])

        # Predict class
        prediction = model.predict(features_array)
        prediction_index = int(prediction[0])
        predicted_class = target_names[prediction_index]

        # Predict probabilities
        if hasattr(model, 'predict_proba'):
            probabilities = model.predict_proba(features_array)[0]
            prob_dict = {
                target_names[i]: float(probabilities[i])
                for i in range(len(target_names))
            }
        else:
            prob_dict = None

        response = {
            'prediction': predicted_class,
            'prediction_index': prediction_index,
            'input_features': {
                feature_names[i]: features[i]
                for i in range(len(features))
            },
            'probabilities': prob_dict
        }

        return jsonify(response)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
