# DEPLOYMENT.md

### Dockerfile
A `Dockerfile` was created in the project root to containerize the FastAPI application using `python:3.10-slim` as the base image. It installs dependencies from `requirements.txt`, sets environment variables, exposes port 8080 (Cloud Run default), and runs the app using Uvicorn.

### .dockerignore
Unnecessary files were excluded using `.dockerignore` to keep the image small and secure:


## Docker Containerization

### Build & local Run
```bash
docker build -t penguin-api .
docker run -p 8080:8080 \
  -v /Users/lanu/Desktop/sa-key.json:/gcp/sa-key.json:ro \
  -e GOOGLE_APPLICATION_CREDENTIALS=/gcp/sa-key.json \
  -e GCS_BUCKET_NAME=penguin-models-lanuja \
  -e GCS_BLOB_NAME=model.json \
  penguin-api


## issues and the solution

module not found error: No module named 'httpx' : Installed httpx (required by FastAPI test client)
No matching distribution found for numpy==2.3.1 : Cleaned up requirements.txt, downgraded to numpy>=1.26.0

403 AccessDeniedException from GCS : Created and used service account key with Storage Object Viewer role

ModuleNotFoundError: No module named 'app' : Added __init__.py and fixed Python path in tests

##  Docker Image Details

- **Image Name**: `penguin-api`
- **Image ID**: `825584e3ee0e`
- **Final Image Size**: 1.57GB
- **Created**: Aug 3, 2025
- **Number of Layers**: 7

##  Layer Summary (from `docker inspect`)

1. Set working directory
2. Install OS-level dependencies (gcc)
3. Upgrade pip
4. Install Python dependencies from `requirements.txt`
5. Copy project files
6. Expose port 8080
7. Start FastAPI with `uvicorn`

Image optimized by using `.dockerignore` and pip `--no-cache-dir` flag.

## Commands Used
1. Build Image for Cloud Run
docker build --platform linux/amd64 -t penguin-api .

2. Tag Image for Artifact Registry
docker tag penguin-api us-central1-docker.pkg.dev/marine-atrium-467613-a4/penguin-repo/penguin-api:latest

3. Authenticate Docker with GCP Artifact Registry
gcloud auth configure-docker us-central1-docker.pkg.dev

4. Push Image to Artifact Registry
docker push us-central1-docker.pkg.dev/marine-atrium-467613-a4/penguin-repo/penguin-api:latest

5. Deploy to Cloud Run (via GCP Console)
Service Name: penguin-api
Image: us-central1-docker.pkg.dev/marine-atrium-467613-a4/penguin-repo/penguin-api:latest
Region: us-central1
Allow unauthenticated invocations
Port: 8080
Environment variables:
GOOGLE_APPLICATION_CREDENTIALS=/gcp/sa-key.json
GCS_BUCKET_NAME=penguin-models-lanuja
GCS_BLOB_NAME=model.json

## Deployment issues and solution
importerror: cannot import name 'app', which was caused by a circular import in main.py. I fixed this by removing the redundant from app.main import app statement.

Billing account not found : This happened because my GCP project did not have billing enabled. I resolved it by linking a billing account to the project in the GCP Console.

500 Internal Server Error because the local image was not tagged as latest. I solved this by rebuilding the image and explicitly tagging it with :latest.

## final URL
https://penguin-api-1086939640536.us-central1.run.app/docs

