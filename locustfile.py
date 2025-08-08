from locust import FastHttpUser, task, between
import os
import json
import random

# ---- Config ----
TARGET_HOST = os.getenv("LOCUST_HOST", "http://localhost:8080")

# Payload generator
def sample_payload():
    sexes = ["male", "female"]
    islands = ["Torgersen", "Biscoe", "Dream"]
    return {
        "bill_length_mm": round(random.uniform(32.0, 60.0), 1),
        "bill_depth_mm": round(random.uniform(13.0, 22.0), 1),
        "flipper_length_mm": random.randint(170, 235),
        "body_mass_g": random.randint(2700, 6300),
        "year": random.choice([2007, 2008, 2009]),
        "sex": random.choice(sexes),
        "island": random.choice(islands),
    }

class PenguinUser(FastHttpUser):
    wait_time = between(0.1, 0.5)
    host = TARGET_HOST

    @task
    def predict(self):
        payload = sample_payload()
        headers = {"Content-Type": "application/json"}
        with self.client.post("/predict", data=json.dumps(payload), headers=headers, name="/predict", catch_response=True) as resp:
            try:
                if resp.status_code != 200:
                    resp.failure(f"HTTP {resp.status_code}")
                else:
                    data = resp.json()
                    if "prediction" not in data:
                        resp.failure("No 'prediction' in response")
                    else:
                        prediction = data["prediction"]
                        resp.success()
                        print(f"✅ Prediction: {prediction}")  # <-- Shows in terminal
            except Exception as e:
                resp.failure(str(e))


