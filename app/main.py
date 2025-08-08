# app/main.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from enum import Enum
import pandas as pd
import json
import xgboost as xgb
import numpy as np
import logging
import os
import base64
from google.cloud import storage  # NEW: Import for GCS

from dotenv import load_dotenv
load_dotenv()


import os
import uvicorn


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))  # fallback to 8080
    uvicorn.run(app, host="0.0.0.0", port=port)


# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Island(str, Enum):
    Torgersen = "Torgersen"
    Biscoe = "Biscoe"
    Dream = "Dream"

class Sex(str, Enum):
    male = "male"
    female = "female"

class PenguinFeatures(BaseModel):
    bill_length_mm: float
    bill_depth_mm: float
    flipper_length_mm: float
    body_mass_g: float
    year: int
    sex: Sex
    island: Island

app = FastAPI()

# Load model.json from GCS instead of local file
GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME")
GCS_BLOB_NAME = os.getenv("GCS_BLOB_NAME")

try:
    client = storage.Client()
    bucket = client.bucket(GCS_BUCKET_NAME)
    blob = bucket.blob(GCS_BLOB_NAME)
    model_json_string = blob.download_as_text()
    model_info = json.loads(model_json_string)
except Exception as e:
    logger.error(f"Failed to load model from GCS: {e}")
    raise RuntimeError("Model loading failed")

# Decode base64-encoded model string into binary
model_base64 = model_info["model"]
model_binary = base64.b64decode(model_base64)

# Load model from binary
booster = xgb.Booster()
booster.load_model(bytearray(model_binary))

# Load columns and reverse label mapping
columns = model_info["columns"]
label_mapping = {v: k for k, v in model_info["label_mapping"].items()}

@app.post("/predict")
def predict(features: PenguinFeatures):
    try:
        input_dict = features.dict()
        df = pd.DataFrame([input_dict])

        # Manual one-hot encoding to match training
        for col in ["sex", "island"]:
            for category in [c for c in columns if c.startswith(col + "_")]:
                df[category] = int(f"{col}_{input_dict[col]}" == category)

        # Drop original non-numeric columns
        df = df.drop(columns=["sex", "island"])

        # Fill missing dummy columns
        for col in columns:
            if col not in df.columns:
                df[col] = 0

        df = df[columns]  # Ensure correct order
        dmatrix = xgb.DMatrix(df)

        pred = booster.predict(dmatrix)
        pred_label = int(np.argmax(pred, axis=1)[0]) if pred.ndim > 1 else int(pred[0])
        predicted_species = label_mapping.get(pred_label, "Unknown")

        logger.info(f"Prediction success: {predicted_species}")
        return {"prediction": predicted_species}

    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        raise HTTPException(status_code=400, detail="Prediction failed. Check input values.")
