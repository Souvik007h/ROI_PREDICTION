from flask import Flask, render_template, request, jsonify
import pandas as pd
import joblib

# ======================================================
# LOAD TRAINED FILES
# ======================================================

model = joblib.load("Model/roi_prediction_model.pkl")
scaler = joblib.load("Model/scaler.pkl")
model_columns = joblib.load("Model/model_columns.pkl")

# ======================================================
# CREATE FLASK APP
# ======================================================

app = Flask(__name__)

# ======================================================
# ORDINAL ENCODING MAPS
# ======================================================

water_map = {
    'Very Low': 0,
    'Low': 1,
    'Medium': 2,
    'High': 3
}

tillage_map = {
    'Zero': 0,
    'Minimum': 1,
    'Conventional': 2
}

season_map = {
    'Rabi': 0,
    'Kharif': 1
}

# ======================================================
# NUMERICAL COLUMNS
# ======================================================

num_cols = [
    'AREA',
    'CROPING',
    'HARVESTING',
    'YIELD',
    'LABOUR',
    'SEEDS',
    'INVESTMENT'
]

# ======================================================
# HOME ROUTE
# ======================================================

@app.route("/")
def home():
    return render_template("index.html")

# ======================================================
# PREDICTION ROUTE
# ======================================================

@app.route("/predict", methods=["POST"])
def predict():

    try:

        # ======================================================
        # GET JSON DATA
        # ======================================================

        data = request.get_json()

        # ======================================================
        # DEFAULT VALUES
        # ======================================================

        input_data = {

            # Numerical Features
            "AREA": float(data.get("AREA", 2.0)),
            "CROPING": 115,
            "HARVESTING": 5,
            "YIELD": float(data.get("YIELD", 3000)),
            "LABOUR": float(data.get("LABOUR", 120)),
            "SEEDS": float(data.get("SEEDS", 30)),
            "INVESTMENT": float(data.get("INVESTMENT", 50000)),

            # Ordinal Encoded Features
            "WATER": water_map.get(data.get("WATER", "Medium"), 2),

            "TILLAGE": tillage_map.get(
                data.get("TILLAGE", "Minimum"),
                1
            ),

            "SEASON": season_map.get(
                data.get("SEASON", "Kharif"),
                1
            )
        }

        # ======================================================
        # CREATE DATAFRAME
        # ======================================================

        df_input = pd.DataFrame([input_data])

        # ======================================================
        # ONE HOT ENCODING
        # ======================================================

        categorical_pairs = {

            "CROP": data.get("CROP", "Rice"),
            "STATE": data.get("STATE", "Punjab"),
            "SOIL": data.get("SOIL", "Loam"),
            "IRRIGATION": data.get("IRRIGATION", "Flood"),
            "FERTIGATION": data.get("FERTIGATION", "Power Sprayer"),
            "SEEDER": data.get("SEEDER", "Manual"),
            "HARVESTOR": data.get("HARVESTOR", "Combine")
        }

        for col, value in categorical_pairs.items():

            column_name = f"{col}_{value}"

            if column_name in model_columns:
                df_input[column_name] = 1

        # ======================================================
        # ADD MISSING COLUMNS
        # ======================================================

        for col in model_columns:

            if col not in df_input.columns:
                df_input[col] = 0

        # ======================================================
        # FIX COLUMN ORDER
        # ======================================================

        df_input = df_input[model_columns]

        # ======================================================
        # SCALE NUMERICAL FEATURES
        # ======================================================

        df_input[num_cols] = scaler.transform(
            df_input[num_cols]
        )

        # ======================================================
        # PREDICT ROI
        # ======================================================

        prediction = model.predict(df_input)[0]

        # ======================================================
        # RETURN RESULT
        # ======================================================

        return jsonify({
            "ROI": round(float(prediction), 2)
        })

    except Exception as e:

        return jsonify({
            "error": str(e)
        })

# ======================================================
# RUN APP
# ======================================================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)