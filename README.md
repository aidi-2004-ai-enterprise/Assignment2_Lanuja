# Penguins XGBoost + FastAPI (Cloud Run)

A production-style ML inference service that serves penguin species predictions via a FastAPI endpoint.  
Model is an XGBoost classifier; the service loads a JSON-serialized model from Google Cloud Storage (GCS) at startup.  
Deployed to Cloud Run, containerized with Docker, tested with pytest, and load-tested with Locust.

---

## Tech Stack
- **Model**: XGBoost (JSON booster)
- **API**: FastAPI + Uvicorn
- **Storage**: Google Cloud Storage
- **Container**: Docker (python:3.10-slim)
- **Hosting**: Cloud Run
- **Testing**: pytest + pytest-cov
- **Load test**: Locust

---
# Quick Start (Local)

1. **Clone the repository**
   ```bash
   git clone https://github.com/<username>/<repo>.git
   cd <repo>
   

2. **Environment**

       ```bash
       python -m venv .venv
       source .venv/bin/activate
       pip install -r requirements.txt

4. **Environment Variables**

   ```bash
   Create a .env file :
   GCS_BUCKET_NAME=penguin-models-<lanuja>
   GCS_BLOB_NAME=model.json

4. **Run locally**

   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8080

Open http://localhost:8080/docs

---

**Run in Docker (Local)**

     ```bash 
    Build
    docker build --platform linux/amd64 -t penguin-api .

Run (mount your SA key read-only)

    ```bash 
    docker run -p 8080:8080 \
    -v /ABSOLUTE/PATH/sa-key.json:/gcp/sa-key.json:ro \
    -e GCS_BUCKET_NAME=penguin-models-<lanuja> \
    -e GCS_BLOB_NAME=model.json \
    penguin-api:latest
---

**Cloud Run (Manual)**

Push image to Artifact Registry:

    ```bash
    docker tag penguin-api us-central1-docker.pkg.dev/<PROJECT_ID>/penguin-repo/penguin-api:latest
    gcloud auth configure-docker us-central1-docker.pkg.dev
    docker push us-central1-docker.pkg.dev/<PROJECT_ID>/penguin-repo/penguin-api:latest
    Create a Secret Manager secret for sa-key.json, mount it at /gcp/sa-key.json.


**Deploy in Cloud Run (console)**:
Image: us-central1-docker.pkg.dev/<PROJECT_ID>/penguin-repo/penguin-api:latest
Port: 8080
Allow unauthenticated (or use ID tokens)
Env vars:

    ```ini
    GOOGLE_APPLICATION_CREDENTIALS=/gcp/sa-key.json
    GCS_BUCKET_NAME=...
    GCS_BLOB_NAME=model.json
---
**API**
POST /predict

Request body (JSON):

    ```json
    {
      "bill_length_mm": 39.1,
      "bill_depth_mm": 18.7,
      "flipper_length_mm": 181,
      "body_mass_g": 3750,
      "year": 2009,
      "sex": "male",
      "island": "Torgersen"
    }

Response:

    ```json
    { "prediction": "Adelie" }

Curl example:

    ```bash
    curl -X POST http://localhost:8080/predict \
    -H "Content-Type: application/json" \
    -d '{"bill_length_mm":39.1,"bill_depth_mm":18.7,"flipper_length_mm":181,"body_mass_g":3750,"year":2009,"sex":"male","island":"Torgersen"}'
---

**Testing**
 
    ```bash
     pytest --cov=app tests/

**Load Testing (Locust)**

Run Locust UI (local):

    ```bash
    LOCUST_HOST=http://localhost:8080 locust
    
Open http://localhost:8089

**Headless examples (cloud)**:

    ```bash
    LOCUST_HOST=https://<your-cloud-run-url> \
    locust -f locustfile.py --headless -u 10 -r 5 -t 5m --csv=results_cloud_normal --only-summary
---

See LOAD_TEST_REPORT.md for results and analysis.
Raw CSVs can be stored under load_results/.


---
# Assignment Answers

1) **What edge cases might break your model in production that aren’t in training data?**
   
Out-of-distribution inputs (extreme lengths/weights, unseen sex/island values).

Missing or wrong types (e.g., strings for numeric fields).

Data drift (real penguin measurements shifting over time).

Malformed JSON or empty payloads.

Mitigation: strict Pydantic validation, boundary checks, default fallbacks, and monitoring for drift/anomalies.

2) **What happens if your model file becomes corrupted?**
   
Load will fail at startup; API should return a 5xx on health/predict if the model isn’t ready.

Mitigation: verify checksum/size before load, fail fast with clear logs, keep a last-known-good model, and add alerting.

3) **What’s a realistic load for a penguin classification service?**
   
Low to moderate (tens–hundreds RPS), depending on usage.
From our tests: locally up to ~150 RPS sustained with zero failures; Cloud Run scaled to 100 users with low p95 latency.

4) **How would you optimize if response times are too slow?**
   
Increase CPU/RAM per instance; tune concurrency.
Keep model in memory, load at startup .
Reduce logging; avoid heavy work on request path.
Consider lighter/quantized models or batching if appropriate.
Enable min instances to avoid cold starts.

5) **What metrics matter most for ML inference APIs?**
   
Latency: p50/p95/p99.
Error rate: 4xx/5xx.
Throughput: RPS.
Resource usage: CPU/RAM per instance.
Cold start count and autoscaling activity.
Input validation failures rate.

6) **Why is Docker layer caching important for build speed? (Did you leverage it?)**
   
Reuses prior layers so i don’t reinstall dependencies or recopy sources unnecessarily → faster builds.
Yes: COPY requirements.txt → pip install → COPY . . leverages cache correctly.

7) **What security risks exist with running containers as root?**
    
Privilege escalation and broader blast radius if compromised.
Mitigation: add a non-root user, read-only filesystem, drop capabilities, mount secrets read-only.

8) **How does cloud auto-scaling affect your load test results?**
    
Smooths spikes by adding instances; p95 latency remains lower under sudden load.
Cold starts may add occasional outliers if min instances is 0.

9) **What would happen with 10x more traffic?**
 
Without scaling: throttling/timeouts and higher p95.
With autoscaling: more instances spin up, higher cost; watch concurrency limits and per-instance CPU.

10) **How would you monitor performance in production?**

Cloud Monitoring dashboards: latency (p50/p95/p99), error rate, RPS, instance CPU/memory.
Structured logs for errors/exceptions; alerts on sustained p95 > threshold or error rate > threshold.

11) **How would you implement blue-green deployment?**
    
Maintain two services/versions (blue/green).
Deploy to green, run smoke tests, then switch traffic (or use Cloud Run revisions with traffic splitting).
Rollback instantly if issues arise.

12) **What would you do if deployment fails in production?**
    
Immediate rollback to last healthy revision.
Inspect logs/metrics, fix root cause in staging, redeploy.
Keep runbooks and alerts for faster MTTR.

13) **What happens if your container uses too much memory?**
    
OOM kill → failures until restart.
Mitigation: monitor usage, reduce footprint, set correct limits.
