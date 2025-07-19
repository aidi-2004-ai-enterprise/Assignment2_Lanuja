# Lab 3: Penguins Classification with XGBoost and FastAPI

---

## Project Overview

This project demonstrates an end-to-end machine learning pipeline using the **Seaborn Penguins** dataset. The workflow includes:

- Preprocessing with one-hot and label encoding  
- Training an XGBoost classifier to predict penguin species  
- Deploying a FastAPI application with a `/predict` endpoint  
- Enforcing input validation using Pydantic and Enums  
- Robust logging and error handling  

---

## 🧪 How to Run the Project

### 1. Clone the Repository

```bash
git clone https://github.com/aidi-2004-ai-enterprise/lab3_lanuja.git
cd lab3_lanuja

2. Set Up and Activate Virtual Environment
uv venv
source .venv/bin/activate

3. Install Dependencies
uv pip install -r requirements.txt
Train the Model

This will:

Load and clean the dataset
Preprocess and encode features
Train an XGBoost classifier
Serialize the model to base64 and save it as app/data/model.json
python train.py
Run the FastAPI Server

uvicorn app.main:app --reload
Access the API documentation at:
http://127.0.0.1:8000/docs

Example Input for /predict

{
  "bill_length_mm": 39.1,
  "bill_depth_mm": 18.7,
  "flipper_length_mm": 181.0,
  "body_mass_g": 3750,
  "year": 2007,
  "sex": "male",
  "island": "Biscoe"
}
Example Response
{
  "species": "Adelie"
}
 Project Structure

penguins-xgboost-fastapi/
├── train.py
├── app/
│   ├── main.py
│   └── data/
│       └── model.json
├── pyproject.toml
├── requirements.txt
├── README.md

Notes

model.json stores a base64-encoded version of the trained XGBoost model for easy JSON loading.
This is a local-only deployment for Lab 3.