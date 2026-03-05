# ===============================
# Professional Backend - Load Trained Model
# ===============================

from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import joblib

app = Flask(__name__)
CORS(app)

# ===============================
# REQUIRED FOR MODEL LOADING
# ===============================

def comma_tokenizer(text):
    return text.split(",")

# ===============================
# SERIOUS DISEASE LIST
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
# LOAD TRAINED MODEL
# ===============================

print("Loading trained model...")

model = joblib.load("model.pkl")
label_encoder = joblib.load("label_encoder.pkl")
medicine_map = joblib.load("medicine_map.pkl")

print("Model loaded successfully!")

# ===============================
# Prediction API
# ===============================

@app.route("/predict", methods=["POST"])
def predict():
    data = request.json

    try:
        age = int(data["age"])
        symptoms = ",".join(data["symptoms"])
    except Exception:
        return jsonify({"error": "Invalid input format"}), 400

    input_data = pd.DataFrame({
        "Age": [age],
        "Symptoms": [symptoms]
    })

    probabilities = model.predict_proba(input_data)[0]
    top_indices = probabilities.argsort()[-3:][::-1]

    results = []

    for index in top_indices:
        disease_name = label_encoder.inverse_transform([index])[0]
        confidence = round(probabilities[index] * 100, 2)

        serious_flag = disease_name.strip().lower() in [
            d.lower() for d in SERIOUS_DISEASES
        ]

        medicines = medicine_map.get(disease_name, "Consult a doctor")

        results.append({
            "disease": disease_name,
            "confidence": confidence,
            "serious": serious_flag,
            "medicines": medicines
        })

    return jsonify(results)

# ===============================

if __name__ == "__main__":
    app.run(debug=True)