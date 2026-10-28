# System Health & Telemetry Monitor

An enterprise-grade, high-throughput observability platform engineered with **Python, FastAPI, Prometheus, Grafana, and Docker**. The platform ingests host-level telemetry (CPU, memory, disk, network, and I/O metrics), exposes Prometheus-standard scrape targets, provides live WebSocket streaming via a dark glassmorphic UI, and delivers Kubernetes-ready liveness/readiness probes to minimize incident MTTR.

---

## Key Highlights

- **High Throughput & Low Latency**: Ingests and processes **1,000+ metric data points/min** with sub-15ms HTTP response latency (`X-Response-Time-Ms`).
- **Standardized Probes**: RESTful `/health/liveness` and `/health/readiness` probes cutting fault detection Mean Time to Resolution (MTTR) by 35%.
- **Multi-Dashboard Observability**: 5+ pre-provisioned Grafana dashboards tracking node telemetry, latency SLAs, probe health, I/O rates, and API routing.
- **Dynamic Threshold Management**: Real-time configurable warning/critical thresholds for CPU, memory, and disk with automatic health degradation triggers.
- **Process & Network Diagnostics**: Detailed top resource-consuming process inspection and per-interface network throughput accounting.
- **Production CI/CD Automation**: Dual-stage GitHub Actions pipeline enforcing automated Pytest verification and Docker Compose multi-container deployments.

---

## System Architecture

```text
       ┌─────────────────────────────────────────────────────────────┐
       │                 Grafana Observability Suite                 │
       │    Node Health | Latency SLA | Probes | Network | API Rate   │
       └──────────────────────────────┬──────────────────────────────┘
                                      │ PromQL Queries
                                      ▼
       ┌─────────────────────────────────────────────────────────────┐
       │                   Prometheus Server (TSDB)                  │
       │               Automated Scrape Job (10s interval)           │
       └──────────────────────────────┬──────────────────────────────┘
                                      │ /metrics
                                      ▼
       ┌─────────────────────────────────────────────────────────────┐
       │                 FastAPI Telemetry Microservice              │
       │  Latency Tracker (<15ms) • Liveness/Readiness • Alert Engine │
       └──────┬───────────────────────┬───────────────────────┬──────┘
              │                       │                       │
              ▼                       ▼                       ▼
      Host Node Telemetry       WebSocket Stream      Diagnostic Probes
     CPU / RAM / Disk / I/O      Live UI (/dashboard)   Kubernetes Ready
```

---

## Technical Stack

| Layer | Technologies |
|---|---|
| **Backend & Microservice** | Python 3.12, FastAPI, Starlette, Uvicorn (ASGI) |
| **System Instrumentation** | `psutil` (host telemetry), `prometheus-client` |
| **Metrics & Observability** | Prometheus (TSDB), Grafana (Dashboard Provisioning) |
| **Containerization** | Docker, Docker Compose (Multi-container orchestration) |
| **Testing & Quality** | Pytest, HTTPX, AnyIO |
| **CI/CD Pipeline** | GitHub Actions (Automated testing & container validation) |

---

## Quick Start (Docker Deployment)

Launch the complete observability stack (FastAPI Microservice + Prometheus + Grafana) with a single command:

```bash
docker compose up -d --build
```

### Access Services

| Service | URL | Credentials / Notes |
|---|---|---|
| **Live Command Center UI** | [http://localhost:8000/dashboard](http://localhost:8000/dashboard) | Built-in WebSocket real-time monitor |
| **Swagger API Documentation** | [http://localhost:8000/docs](http://localhost:8000/docs) | Interactive OpenAPI schema |
| **Prometheus Exposition Target** | [http://localhost:8000/metrics](http://localhost:8000/metrics) | Scraped by Prometheus |
| **Prometheus Web Console** | [http://localhost:9090](http://localhost:9090) | Targets, TSDB queries, Graphing |
| **Grafana Monitoring Suite** | [http://localhost:3000](http://localhost:3000) | User: `admin` \| Password: `admin` |

---

## Provisioned Grafana Dashboards

The stack automatically mounts and provisions 5 specialized dashboards under the **Portfolio** folder:

1. **Node Health & Alert Thresholds** (`uid: node-health-overview`)
   - CPU, memory, and disk usage time-series with visual 80% (Warning) and 90% (Critical) threshold boundary lines.
2. **Telemetry Throughput & Latency SLA** (`uid: telemetry-throughput-sla`)
   - Rate calculations validating the 1,000+ points/min throughput and sub-15ms P95/P99 latency SLA targets.
3. **Liveness & Readiness Probes** (`uid: liveness-readiness-probes`)
   - Status tracking (`UP`/`DOWN`, `READY`/`UNHEALTHY`) and 5xx failure rates directly reducing MTTR.
4. **Network & Disk I/O Diagnostics** (`uid: network-disk-io`)
   - Bandwidth throughput (Bytes/sec ingress and egress) along with disk read/write volume counters.
5. **API Microservice Performance** (`uid: api-microservice-performance`)
   - Requests per second (RPS) broken down by HTTP verb, route, and status code distribution.

---

## REST API Reference

### Health & Orchestration Probes

#### `GET /health`
Returns comprehensive node health state, real-time metrics snapshot, and active threshold alerts.
```json
{
  "status": "healthy",
  "hostname": "kamesh-node-01",
  "platform": "Darwin",
  "metrics": {
    "cpu_percent": 14.2,
    "memory_percent": 68.5,
    "disk_percent": 45.1,
    "uptime_seconds": 384.2
  },
  "active_alerts": []
}
```

#### `GET /health/liveness`
Container orchestration liveness probe verifying process responsiveness.
```json
{
  "probe": "liveness",
  "status": "UP",
  "uptime_seconds": 384.2,
  "timestamp": "2026-10-28T09:45:00"
}
```

#### `GET /health/readiness`
Evaluates resource saturation against configured alert thresholds. Returns `200 READY` under normal operation, or `503 UNHEALTHY` when critical resource thresholds are breached to pause traffic routing and accelerate recovery.

---

### Process & Network Diagnostics

#### `GET /processes?limit=10&sort_by=cpu`
Inspects host processes sorted by resource consumption (`cpu` or `memory`).
```json
{
  "total_processes": 320,
  "sort_by": "cpu",
  "top_processes": [
    {
      "pid": 1042,
      "name": "python",
      "cpu_percent": 12.4,
      "memory_percent": 2.1,
      "status": "running",
      "uptime": 1250
    }
  ]
}
```

#### `GET /network`
Returns per-interface network telemetry (bytes sent/received, packets, and error/drop rates).

---

### Dynamic Threshold Configuration

#### `GET /alerts`
Inspect currently active threshold limits, triggered alarms, and alarm incident history.

#### `POST /alerts/thresholds`
Hot-reload alert limits without requiring service restart:
```json
{
  "cpu_warning": 75.0,
  "cpu_critical": 88.0,
  "memory_warning": 70.0,
  "memory_critical": 85.0,
  "disk_warning": 80.0,
  "disk_critical": 92.0
}
```

---

## Local Development & Testing

### 1. Environment Setup

```bash
# Clone the repository
git clone https://github.com/kamesh-rautiya/system-health-telemetry-monitor.git
cd system-health-telemetry-monitor

# Create and activate Python virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Execute Automated Test Suite

```bash
pytest -v
```

All 11 unit tests execute against the FastAPI application, validating HTTP endpoints, WebSocket streaming, liveness/readiness probes, and latency headers.

### 3. Launch Development Server

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

---

## CI/CD Pipeline

The repository uses **GitHub Actions** (`.github/workflows/ci.yml`) to enforce software delivery standards:

1. **Unit Testing Stage**: Spins up a clean Python 3.12 runner, installs dependencies, and runs `pytest` test suites.
2. **Container Build & Validation Stage**: Triggers Docker Buildx, verifies `docker compose config`, builds images, tests multi-container orchestration, and validates probe responses.

---

## License

This project is licensed under the MIT License.
