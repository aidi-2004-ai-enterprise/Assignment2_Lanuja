# LOAD_TEST_REPORT

## Overview
We used Locust to evaluate the FastAPI + XGBoost prediction service locally (Docker) and on Cloud Run.

**Targets**
- Local: http://localhost:8089
- Cloud: https://https://penguin-api-1086939640536.us-central1.run.app

**Test Scenarios**
- Baseline (1 user, 60s) - local and cloud
- Normal (10 users, 5m) - local and cloud
- Stress (50 users, 2m) — Cloud only
- Spike (1 → 100 users in ~1m) — Cloud only

---

## Results Summary

| Scenario  | Env    | Users | Duration | Avg Latency (ms) | P95 (ms) | RPS | Fail % |
|-----------|--------|-------|----------|------------------|----------|-----|--------|
| Baseline  | Local  | 1     | 60s      |     59.02        |    70    | 2.7 |    0   |
| Normal    | Local  | 10    | 5m       |    206.57        |    440   | 1.7 |    0   |
| Baseline  | Cloud  | 1     | 60s      |       78         |    93    | 2.7 |    0   |
| Normal    | Cloud  | 10    | 5m       |      75.5        |    99    |  27 |    0   |
| Stress    | Cloud  | 50    | 2m       |     112.42       |    280   |128.8|    0   |
| Spike     | Cloud  | 100   | ~1m      |      84.04       |    130   |148.8|    0   |

Notes:
- P95 = 95th percentile response time
- RPS = requests per second (throughput)


---

## Observations
- **Zero failures** in all scenarios.
- **Cloud Run scaled efficiently**, maintaining low latency up to 100 concurrent users.
- Local environment showed higher latency under moderate load due to resource constraints.

---

## Bottlenecks
- Local CPU and memory limits impact throughput.
- JSON parsing and model inference contribute to latency.
- Minor network overhead in Cloud Run baseline runs.

---

## Recommendations
1. Configure **min-instances=1** in Cloud Run to reduce cold starts.
2. Increase **max-instances** and set concurrency to **80–100** for handling spikes.
3. Allocate **1–2 vCPU** and **1–2 GB RAM** for lower p95 latency.
4. Reduce logging verbosity at high traffic.
5. Monitor **p95 latency**, **error rates**, and **scaling metrics** via Cloud Monitoring.

---