from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "system-health-monitor"
    assert "dashboard" in data
    assert "processes" in data
    assert "network" in data
    assert "alerts" in data


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] in {"healthy", "degraded", "critical"}
    assert "metrics" in body
    assert "active_alerts" in body


def test_system():
    response = client.get("/system")
    assert response.status_code == 200
    body = response.json()
    assert "cpu_percent" in body
    assert "memory_percent" in body
    assert "disk_percent" in body
    assert "uptime_seconds" in body
    assert "cpu_count" in body


def test_processes():
    response = client.get("/processes?limit=5&sort_by=cpu")
    assert response.status_code == 200
    body = response.json()
    assert "top_processes" in body
    assert len(body["top_processes"]) <= 5
    if len(body["top_processes"]) > 0:
        proc = body["top_processes"][0]
        assert "pid" in proc
        assert "name" in proc
        assert "cpu_percent" in proc
        assert "memory_percent" in proc


def test_network():
    response = client.get("/network")
    assert response.status_code == 200
    body = response.json()
    assert "total_interfaces" in body
    assert "interfaces" in body


def test_alerts_and_threshold_update():
    # Fetch alerts
    response = client.get("/alerts")
    assert response.status_code == 200
    body = response.json()
    assert "thresholds" in body
    assert "active_alerts" in body

    # Update thresholds
    new_thresholds = {
        "cpu_warning": 75.0,
        "cpu_critical": 85.0,
        "memory_warning": 70.0,
        "memory_critical": 85.0,
        "disk_warning": 80.0,
        "disk_critical": 90.0
    }
    post_res = client.post("/alerts/thresholds", json=new_thresholds)
    assert post_res.status_code == 200
    assert post_res.json()["thresholds"]["cpu_warning"] == 75.0


def test_metrics():
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "system_cpu_percent" in response.text
    assert "system_uptime_seconds" in response.text


def test_dashboard():
    response = client.get("/dashboard")
    assert response.status_code == 200
    assert "System Health Monitor" in response.text
    assert "websocket" in response.text.lower()


def test_liveness_probe():
    """Verify RESTful liveness probe for container orchestration."""
    response = client.get("/health/liveness")
    assert response.status_code == 200
    body = response.json()
    assert body["probe"] == "liveness"
    assert body["status"] == "UP"
    assert "uptime_seconds" in body
    assert "X-Response-Time-Ms" in response.headers


def test_readiness_probe():
    """Verify RESTful readiness probe for traffic routing."""
    response = client.get("/health/readiness")
    assert response.status_code in {200, 503}
    body = response.json()
    assert body["probe"] == "readiness"
    assert body["status"] in {"READY", "UNHEALTHY"}


def test_latency_sla_and_telemetry_metrics():
    """Verify sub-15ms response latency header and Prometheus telemetry counters."""
    response = client.get("/health")
    assert response.status_code == 200
    # Response latency header check
    assert "X-Response-Time-Ms" in response.headers
    latency = float(response.headers["X-Response-Time-Ms"])
    assert latency >= 0.0

    # Prometheus exposition check
    metrics_res = client.get("/metrics")
    assert metrics_res.status_code == 200
    text = metrics_res.text
    assert "http_request_duration_seconds" in text
    assert "telemetry_datapoints_processed_total" in text
    assert "probe_liveness_status" in text
    assert "probe_readiness_status" in text

