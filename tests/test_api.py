# tests/test_api.py
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from app.main import app  # Update this path if your app is in a different location
import pytest

client = TestClient(app)

def test_predict_valid_input():
    sample_data = {
        "bill_length_mm": 39.1,
        "bill_depth_mm": 18.7,
        "flipper_length_mm": 181,
        "body_mass_g": 3750,
        "year": 2009,
        "sex": "male",
        "island": "Torgersen"
    }
    response = client.post("/predict", json=sample_data)
    assert response.status_code == 200
    assert "prediction" in response.json()

def test_predict_missing_field():
    sample_data = {
        "bill_length_mm": 39.1,
        "bill_depth_mm": 18.7,
        "flipper_length_mm": 181
        # missing body_mass_g
    }
    response = client.post("/predict", json=sample_data)
    assert response.status_code == 422

def test_predict_invalid_type():
    sample_data = {
        "bill_length_mm": "thirty-nine",  # invalid string
        "bill_depth_mm": 18.7,
        "flipper_length_mm": 181,
        "body_mass_g": 3750,
        "year": 2009,
        "sex": "male",
        "island": "Torgersen"
    }
    response = client.post("/predict", json=sample_data)
    assert response.status_code == 422

def test_predict_extreme_values():
    sample_data = {
        "bill_length_mm": 9999.9,
        "bill_depth_mm": 0.0,
        "flipper_length_mm": -100,
        "body_mass_g": -5000,
        "year": 2009,
        "sex": "male",
        "island": "Torgersen"
    }
    response = client.post("/predict", json=sample_data)
    assert response.status_code == 200
    assert "prediction" in response.json()
