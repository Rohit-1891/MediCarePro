# ===============================
# Professional Backend - Load Trained Model
# Ready for Render Deployment
# ===============================

from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import joblib
import os  # For dynamic PORT

app = Flask(__name__)
CORS(app)  # Allow frontend requests

# ===============================
# Helper function for symptom tokenization
# ===============================
def comma_tokenizer(text):
    return text.split(",")

# ===============================
# Serious disease list
# ===============================
SERIOUS_DISEASES = [
    "Diabetes",
    "Hypertension",
    "Asthma",
    "Tuberculosis",
    "Hepatitis A",
    "Hepatitis B",
    "Dengue",
    "Malaria",
    "Heart Disease",
    "COPD",
    "Liver Cirrhosis",
    "Pneumonia",
    "Influenza (Severe)",
    "COVID-19"
]

# ===============================
# Load trained models and mappings
# ===============================
print("Loading trained model...")
try:
    model = joblib.load("model.pkl")
    label_encoder = joblib.load("label_encoder.pkl")
    medicine_map = joblib.load("medicine_map.pkl")
    print("Model loaded successfully!")
except Exception as e:
    print(f"Error loading model files: {e}")
    raise e

# ===============================
# Prediction API
# ===============================

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "MediCarePro Backend is Running",
        "status": "success"
    })

@app.route("/predict", methods=["POST"])
def predict():
    data = request.json

    # Validate input
    if not data or "age" not in data or "symptoms" not in data:
        return jsonify({"error": "Missing 'age' or 'symptoms' in request"}), 400

    try:
        age = int(data["age"])
        if not isinstance(data["symptoms"], list):
            return jsonify({"error": "'symptoms' should be a list"}), 400
        symptoms = ",".join(data["symptoms"])
    except Exception as e:
        return jsonify({"error": f"Invalid input format: {e}"}), 400

    # Prepare input dataframe
    input_data = pd.DataFrame({
        "Age": [age],
        "Symptoms": [symptoms]
    })

    # Predict probabilities
    probabilities = model.predict_proba(input_data)[0]
    top_indices = probabilities.argsort()[-3:][::-1]

    results = []
    for index in top_indices:
        disease_name = label_encoder.inverse_transform([index])[0]
        confidence = round(probabilities[index] * 100, 2)
        serious_flag = disease_name.strip().lower() in [d.lower() for d in SERIOUS_DISEASES]
        medicines = medicine_map.get(disease_name, "Consult a doctor")

        results.append({
            "disease": disease_name,
            "confidence": confidence,
            "serious": serious_flag,
            "medicines": medicines
        })

    return jsonify(results)

# ===============================
# Run server
# ===============================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)