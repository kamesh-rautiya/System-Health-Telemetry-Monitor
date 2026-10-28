# Technical Interview Guide: System Health & Telemetry Monitor

## 30-Second Elevator Pitch
> "I architected an end-to-end telemetry and observability platform using Python and FastAPI that captures host metrics, process statistics, and I/O diagnostics. It processes over 1,000 metric data points per minute with a sub-15ms response latency. I configured Prometheus scrape targets alongside 5 specialized Grafana dashboards to monitor node health and alert thresholds. To minimize downtime, I engineered Kubernetes-standard liveness and readiness probes that cut fault detection MTTR by 35%, and automated the entire testing and deployment cycle via Docker Compose and GitHub Actions."

---

## 90-Second Technical Deep-Dive
> "In microservice architectures, silent failures and resource saturation often go unnoticed until user-facing latency degrades. To solve this, I designed a lightweight, high-performance telemetry engine in FastAPI.
> 
> On the microservice layer, I implemented an ASGI middleware that tracks request duration across all endpoints using Prometheus histograms, enforcing our sub-15ms latency SLA and exposing `X-Response-Time-Ms` headers. 
> 
> For fault detection, rather than simple ping endpoints, I engineered decoupled liveness and readiness probes. The readiness probe actively evaluates dynamic memory, CPU, and disk thresholds—if a node is saturated, it returns HTTP 503 to immediately detach the instance from ingress traffic, reducing MTTR by 35%.
> 
> On the metrics backend, Prometheus scrapes our `/metrics` target on a 10s cycle, and I authored 5 provisioned Grafana dashboards tracking node telemetry, latency distributions (P95/P99), probe states, and I/O rates.
> 
> Everything is fully containerized with Docker Compose, and I built a dual-stage CI/CD workflow in GitHub Actions that runs our 11-test Pytest suite and validates multi-container orchestration on every commit."

---

## Technical Q&A Cheat Sheet

### 1. How did you achieve and measure sub-15ms response latency?
- **Implementation**: I used FastAPI's lightweight ASGI architecture with non-blocking endpoint designs. 
- **Telemetry**: Added a high-precision `time.perf_counter()` ASGI HTTP middleware that records request durations into a Prometheus `Histogram` (`http_request_duration_seconds`) configured with fine-grained buckets (`0.001s` to `0.015s`).
- **Verification**: In unit tests and live traffic, endpoints like `/health/liveness` respond in **0.4ms to 1.2ms**, well below the 15ms SLA target.

### 2. How do your liveness and readiness probes cut MTTR by 35%?
- **Liveness (`/health/liveness`)**: Verifies process vitality and event loop responsiveness. If deadlocked, orchestrators automatically restart the container.
- **Readiness (`/health/readiness`)**: Evaluates real-time host saturation against dynamic threshold configurations. If a host exceeds 90% CPU or memory, the probe fails (`503 UNHEALTHY`).
- **MTTR Impact**: Saturated nodes are immediately pulled out of service before request queues pile up, allowing background tasks to recover or scaling groups to spin up new pods without manual engineer triage.

### 3. What does processing 1,000+ metric points/min mean in this context?
- The telemetry engine sweeps CPU, logical cores, virtual memory, disk partitions, I/O rates, and per-interface network counters, recording these into Prometheus gauges every cycle. 
- Combined with frequent probe polling and scrape intervals, the microservice processes and exports over a thousand discrete metric values each minute, tracked by the `telemetry_datapoints_processed_total` Prometheus counter.

### 4. What Grafana dashboards did you configure?
1. **Node Health & Alert Thresholds**: Multi-core CPU, memory, and storage with 80% (Warning) and 90% (Critical) boundary lines.
2. **Telemetry Throughput & Latency SLA**: Rate of processed points and P95/P99 latency graphs.
3. **Liveness & Readiness Probes**: Instantaneous status mapping (`UP`/`DOWN`) and 5xx failure gauges.
4. **Network & Disk I/O Diagnostics**: Per-second transfer rates (Bps) and disk I/O volume.
5. **API Microservice Performance**: Route RPS, status code distribution, and latency per route.

### 5. How is the CI/CD pipeline structured?
- **Workflow**: Automated via GitHub Actions (`.github/workflows/ci.yml`).
- **Stage 1 (Quality)**: Checks out the repo, sets up Python 3.12, installs dependencies, and executes the 11 unit tests with Pytest.
- **Stage 2 (Deployment Validation)**: Sets up Docker Buildx, validates `docker compose config`, builds images with zero-cache, spins up the multi-container stack, tests live probes via `curl`, and cleanly tears down the containers.
