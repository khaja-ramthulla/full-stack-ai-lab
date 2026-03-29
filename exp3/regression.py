from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import pandas as pd
import pickle

# Load the Iris dataset
print("Loading Iris dataset...")
iris = load_iris()

X = iris.data
y = iris.target

# Display dataset information
print(f"\nDataset shape: {X.shape}")
print(f"Number of classes: {len(iris.target_names)}")
print(f"Classes: {iris.target_names}")
print(f"Feature names: {iris.feature_names}")

# Create DataFrame for visualization
df = pd.DataFrame(X, columns=iris.feature_names)
df["species"] = y

print("\nFirst 5 rows of dataset:")
print(df.head())

# Split the dataset (80% train, 20% test)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print(f"\nTraining set size: {X_train.shape[0]}")
print(f"Testing set size: {X_test.shape[0]}")

# Train Logistic Regression model
print("\nTraining Logistic Regression model...")
model = LogisticRegression(max_iter=200)
model.fit(X_train, y_train)

# Make predictions
y_pred = model.predict(X_test)

# Evaluate the model
accuracy = accuracy_score(y_test, y_pred)
print(f"\nModel Accuracy: {accuracy * 100:.2f}%")

print("\nClassification Report:")
print(classification_report(y_test, y_pred, target_names=iris.target_names))

print("\nConfusion Matrix:")
print(confusion_matrix(y_test, y_pred))

# Save the model
model_filename = "iris_logistic_regression.pkl"
with open(model_filename, "wb") as file:
    pickle.dump(model, file)

print(f"\nModel saved as '{model_filename}'")

# Save feature names
with open("feature_names.pkl", "wb") as file:
    pickle.dump(iris.feature_names, file)

# Save target names
with open("target_names.pkl", "wb") as file:
    pickle.dump(iris.target_names, file)

print("Feature names and target names saved.")

# Test loading the model
print("\nTesting model loading...")
with open(model_filename, "rb") as file:
    loaded_model = pickle.load(file)

# Sample prediction
sample = [[5.1, 3.5, 1.4, 0.2]]
prediction = loaded_model.predict(sample)

print(f"\nSample input: {sample}")
print(f"Predicted class: {iris.target_names[prediction[0]]}")
