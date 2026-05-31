import time
import threading
import requests
import numpy as np
from sklearn.ensemble import IsolationForest
from collections import deque
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

PROMETHEUS_URL = "http://prometheus:9090"
SCRAPE_INTERVAL = 15
WINDOW_SIZE = 50

# ML Data Buffer
traffic_data = deque(maxlen=WINDOW_SIZE)
anomaly_score = 0.0
model = IsolationForest(contamination=0.1, random_state=42)
model_trained = False

def get_metric(query):
    try:
        r = requests.get(f"{PROMETHEUS_URL}/api/v1/query", params={"query": query}, timeout=5)
        data = r.json()
        if data["status"] == "success" and data["data"]["result"]:
            return float(data["data"]["result"][0]["value"][1])
        return 0.0
    except Exception as e:
        logger.error(f"Prometheus Error: {e}")
        return 0.0

def collect_metrics():
    rx = get_metric('rate(node_network_receive_bytes_total{device="eth0"}[1m])')
    tx = get_metric('rate(node_network_transmit_bytes_total{device="eth0"}[1m])')
    cpu = get_metric('100 - (avg(rate(node_cpu_seconds_total{mode="idle"}[1m])) * 100)')
    return [rx, tx, cpu]

def train_and_detect():
    global anomaly_score, model_trained

    while True:
        try:
            metrics = collect_metrics()
            traffic_data.append(metrics)

            logger.info(f"Metrics — RX: {metrics[0]:.0f} B/s | TX: {metrics[1]:.0f} B/s | CPU: {metrics[2]:.1f}%")

            if len(traffic_data) >= 20:
                X = np.array(list(traffic_data))
                model.fit(X)
                model_trained = True

                score = model.decision_function([metrics])[0]
                # Normalize the score between 0 and 1 (1 = definite anomaly)
                anomaly_score = max(0.0, min(1.0, -score + 0.5))

                if anomaly_score > 0.7:
                    logger.warning(f"ANOMALY DETECTED! Score: {anomaly_score:.3f} | Metrics: {metrics}")
                else:
                    logger.info(f"Normal — Anomaly Score: {anomaly_score:.3f}")

        except Exception as e:
            logger.error(f"Detection Error: {e}")

        time.sleep(SCRAPE_INTERVAL)

# HTTP Server for Prometheus scrape + Alertmanager webhook
class MetricsHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path == "/metrics":
            output = f"""# HELP ml_anomaly_score ML anomaly score (0=normal, 1=anomaly)
# TYPE ml_anomaly_score gauge
ml_anomaly_score {anomaly_score:.4f}

# HELP ml_model_trained ML model training status
# TYPE ml_model_trained gauge
ml_model_trained {1 if model_trained else 0}
"""
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(output.encode())

        elif self.path == "/health":
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")

    def do_POST(self):
        if self.path == "/alert":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)
            try:
                alert = json.loads(body)
                logger.warning(f"ALERT RECEIVED: {json.dumps(alert, indent=2)}")
            except Exception as e:
                logger.error(f"Failed to parse alert JSON: {e}")
                pass
            self.send_response(200)
            self.end_headers()

    def log_message(self, format, *args):
        pass  # Suppress default HTTP logs

def run_server():
    server = HTTPServer(("0.0.0.0", 8000), MetricsHandler)
    logger.info("ML Detector started on port 8000")
    server.serve_forever()

if __name__ == "__main__":
    logger.info("Starting Monitoring ML Detector...")

    # Thread for ML training and detection
    t = threading.Thread(target=train_and_detect, daemon=True)
    t.start()

    # Main HTTP Server
    run_server()
