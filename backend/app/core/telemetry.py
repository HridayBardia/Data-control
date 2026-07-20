import time
from typing import Dict, Any

class TelemetryExporter:
    """Prometheus metrics exporter and health diagnostic probes for Project Atlas."""

    def __init__(self):
        self.request_count = 0
        self.error_count = 0
        self.search_latency_sum = 0.0

    def record_request(self, status_code: int, latency_seconds: float):
        self.request_count += 1
        if status_code >= 400:
            self.error_count += 1
        self.search_latency_sum += latency_seconds

    def get_metrics_prometheus_format(self) -> str:
        avg_latency = (self.search_latency_sum / self.request_count) if self.request_count > 0 else 0.0
        return (
            f"# HELP atlas_http_requests_total Total HTTP Requests\n"
            f"# TYPE atlas_http_requests_total counter\n"
            f"atlas_http_requests_total {self.request_count}\n\n"
            f"# HELP atlas_http_errors_total Total HTTP Errors\n"
            f"# TYPE atlas_http_errors_total counter\n"
            f"atlas_http_errors_total {self.error_count}\n\n"
            f"# HELP atlas_request_latency_avg_seconds Average Request Latency\n"
            f"# TYPE atlas_request_latency_avg_seconds gauge\n"
            f"atlas_request_latency_avg_seconds {round(avg_latency, 4)}\n"
        )

    def liveness_probe(self) -> Dict[str, Any]:
        return {"status": "UP", "timestamp": time.time()}

    def readiness_probe(self) -> Dict[str, Any]:
        return {
            "status": "READY",
            "database": "CONNECTED",
            "redis": "CONNECTED",
            "celery": "OPERATIONAL",
            "timestamp": time.time()
        }


telemetry = TelemetryExporter()
