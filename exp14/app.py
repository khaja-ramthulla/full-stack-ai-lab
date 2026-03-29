from flask import Flask, request, render_template, jsonify
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import pandas as pd
from sklearn.linear_model import LinearRegression

# Load .env variables
load_dotenv()

mongo_uri = os.getenv("MONGO_URI")
db_name = os.getenv("DB_NAME")
collection_name = os.getenv("COLLECTION_NAME")
secret_key = os.getenv("SECRET_KEY")
port = int(os.getenv("PORT", 5000))

app = Flask(__name__)
app.config["SECRET_KEY"] = secret_key

# MongoDB connection
client = MongoClient(mongo_uri)
db = client[db_name]
collection = db[collection_name]


@app.route("/")
def home():
    return render_template("form.html")


@app.route("/submit", methods=["POST"])
def submit():
    try:
        hours = float(request.form["hours"])
        score = float(request.form["score"])

        collection.insert_one({
            "hours": hours,
            "score": score
        })

        return jsonify({"message": "✅ Data stored successfully!"})

    except Exception as e:
        return jsonify({"message": f"❌ Error: {str(e)}"})


@app.route("/train")
def train_model():
    try:
        data = list(collection.find({}, {"_id": 0}))

        if len(data) == 0:
            return jsonify({"message": "⚠️ No data found. Please submit data first."})

        df = pd.DataFrame(data)

        X = df[["hours"]]
        y = df["score"]

        model = LinearRegression()
        model.fit(X, y)

        prediction = model.predict([[5]])

        return jsonify({
            "message": f"📊 Prediction for studying 5 hours = {round(prediction[0],2)}"
        })

    except Exception as e:
        return jsonify({"message": f"❌ Training error: {str(e)}"})


if __name__ == "__main__":
    app.run(debug=True, port=port)