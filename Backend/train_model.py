# ===============================
# Train Model + Evaluation + Save
# ===============================

import pandas as pd
import joblib
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

# Required for loading model later
def comma_tokenizer(text):
    return text.split(",")

print("Loading dataset...")

df = pd.read_csv("disease_dataset_3000_rows.csv")
df = df.dropna()

# ===============================
# SAVE MEDICINE MAPPING
# ===============================
disease_medicine_map = df.groupby("Disease")["Medicines"].first().to_dict()

# ===============================
# Features & Target
# ===============================
X = df[["Age", "Symptoms"]]
y = df["Disease"]

label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
)

print("Data split completed.")
print("Training samples:", len(X_train))
print("Testing samples:", len(X_test))

# ===============================
# Preprocessing
# ===============================
preprocessor = ColumnTransformer(
    transformers=[
        ("symptoms", CountVectorizer(tokenizer=comma_tokenizer), "Symptoms"),
        ("age", "passthrough", ["Age"])
    ]
)

model = Pipeline(steps=[
    ("preprocessing", preprocessor),
    ("classifier", RandomForestClassifier(n_estimators=200, random_state=42))
])

print("Training model...")
model.fit(X_train, y_train)

# ===============================
# MODEL EVALUATION
# ===============================
print("\nEvaluating model...")

y_pred = model.predict(X_test)

accuracy = accuracy_score(y_test, y_pred)

print("\n===============================")
print("Model Accuracy:", round(accuracy * 100, 2), "%")
print("===============================\n")

print("Classification Report:\n")
print(classification_report(y_test, y_pred, target_names=label_encoder.classes_))

print("Confusion Matrix:\n")
print(confusion_matrix(y_test, y_pred))

# ===============================
# SAVE TRAINED MODEL
# ===============================
joblib.dump(model, "model.pkl")
joblib.dump(label_encoder, "label_encoder.pkl")
joblib.dump(disease_medicine_map, "medicine_map.pkl")

print("\nModel and medicine map saved successfully!")