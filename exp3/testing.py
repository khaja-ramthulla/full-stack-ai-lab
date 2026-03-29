import pickle

# Model details
model_name = "Logistic Regression"
model_file = "iris_logistic_regression.pkl"

# Load supporting files
with open("feature_names.pkl", "rb") as f:
    feature_names = pickle.load(f)

with open("target_names.pkl", "rb") as f:
    target_names = pickle.load(f)

print("Feature Names:", feature_names)
print("Target Names:", target_names)

# Test samples
test_samples = [
    [5.1, 3.5, 1.4, 0.2],  # Likely Setosa
    [6.7, 3.0, 5.2, 2.3],  # Likely Virginica
    [5.7, 2.8, 4.1, 1.3]   # Likely Versicolor
]

print("\n" + "=" * 50)
print(f"Testing {model_name}")
print("=" * 50)

# Load model
with open(model_file, "rb") as f:
    model = pickle.load(f)

# Predict samples
for i, sample in enumerate(test_samples, start=1):
    prediction = model.predict([sample])
    print(f"\nSample {i}: {sample}")
    print(f"Predicted Class: {target_names[prediction[0]]}")
