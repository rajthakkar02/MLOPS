from flask import Flask, request, jsonify
import joblib
import pandas as pd
import sqlite3
from waitress import serve
import os

app = Flask(__name__)

DB_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DB_DIR, exist_ok=True)
DB_PATH = os.path.join(DB_DIR, "churn.db")

model = joblib.load("churn_pipeline.pkl")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute("""
    CREATE TABLE IF NOT EXISTS customer_predictions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        gender TEXT,
        SeniorCitizen INTEGER,
        Partner TEXT,
        Dependents TEXT,
        tenure INTEGER,
        PhoneService TEXT,
        MultipleLines TEXT,
        InternetService TEXT,
        OnlineSecurity TEXT,
        OnlineBackup TEXT,
        DeviceProtection TEXT,
        TechSupport TEXT,
        StreamingTV TEXT,
        StreamingMovies TEXT,
        Contract TEXT,
        PaperlessBilling TEXT,
        PaymentMethod TEXT,
        MonthlyCharges REAL,
        TotalCharges REAL,
        prediction TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    conn.commit()
    conn.close()


init_db()


@app.route("/health")
def health():
    return jsonify({"status": "API running"})


@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json(force=True, silent=True)

        if not data:
            return jsonify({"error": "No input data received"}), 400

        data["SeniorCitizen"] = int(data["SeniorCitizen"])
        data["tenure"] = int(data["tenure"])
        data["MonthlyCharges"] = float(data["MonthlyCharges"])
        data["TotalCharges"] = float(data["TotalCharges"])

        input_df = pd.DataFrame([data])
        pred = model.predict(input_df)[0]
        result = "Customer Will Churn" if pred == 1 else "Customer Will Stay"

        conn = get_db()
        conn.execute("""
        INSERT INTO customer_predictions (
            gender, SeniorCitizen, Partner, Dependents, tenure,
            PhoneService, MultipleLines, InternetService,
            OnlineSecurity, OnlineBackup, DeviceProtection,
            TechSupport, StreamingTV, StreamingMovies,
            Contract, PaperlessBilling, PaymentMethod,
            MonthlyCharges, TotalCharges, prediction
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            data.get("gender"),
            data.get("SeniorCitizen"),
            data.get("Partner"),
            data.get("Dependents"),
            data.get("tenure"),
            data.get("PhoneService"),
            data.get("MultipleLines"),
            data.get("InternetService"),
            data.get("OnlineSecurity"),
            data.get("OnlineBackup"),
            data.get("DeviceProtection"),
            data.get("TechSupport"),
            data.get("StreamingTV"),
            data.get("StreamingMovies"),
            data.get("Contract"),
            data.get("PaperlessBilling"),
            data.get("PaymentMethod"),
            data.get("MonthlyCharges"),
            data.get("TotalCharges"),
            result
        ))
        conn.commit()
        conn.close()

        return jsonify({"prediction": result})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/history", methods=["GET"])
def history():
    try:
        conn = get_db()
        rows = conn.execute(
            "SELECT * FROM customer_predictions ORDER BY created_at DESC"
        ).fetchall()
        conn.close()
        return jsonify([dict(row) for row in rows])

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    print("Backend API running at http://localhost:5001")
    serve(app, host="0.0.0.0", port=5001)