import time
import random
import csv
import threading

from flask import Flask, request, jsonify
app = Flask(__name__)

# Set certificates
NUM_CERTS_TO_ISSUE = 1000

@app.route("/", methods=["GET"])
def home():
    return "SCMS Flask API is running"

cert_store = []
log_file = "sc`ms`_report.csv"
summary_file = "scms_summary.csv"
total_issue_time = 0.0
total_verify_time = 0.0
lock = threading.Lock()

def init_log_files():
    with open(log_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Operation", "Certificate", "ProcessingTime(ms)", "Status"])
    with open(summary_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["TotalIssued", "TotalVerified", "TotalIssueTime(ms)", "TotalVerifyTime(ms)", "TotalProcessingTime(ms)", "AverageTimePerCertificate(ms)"])

def log_result(operation, cert, time_spent, status):
    with open(log_file, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([operation, cert, f"{time_spent:.3f}", status])

def artificial_delay(): # 10 ms
    time.sleep(0.01)

# Issue single certificate
@app.route("/issue", methods=["POST"])
def issue_certificate():
    global total_issue_time

    start = time.perf_counter()
    cert = f"CERT: {random.randint(0, 100000)}"

    with lock:
        cert_store.append(cert)

    artificial_delay()
    time_spent = (time.perf_counter() - start) * 1000

    with lock:
        total_issue_time += time_spent

    log_result("Issue", cert, time_spent, "Issued")
    return jsonify({"certificate": cert, "time_ms": round(time_spent, 3), "status": "Issued"})

# Issue certificates in bulk
@app.route("/bulk-issue", methods=["POST"])
def bulk_issue():
    results = []
    for _ in range(NUM_CERTS_TO_ISSUE):
        resp = issue_certificate()
        results.append(resp.get_json())
    return jsonify(results)

@app.route("/verify", methods=["POST"])
def verify_certificate():
    global total_verify_time
    data = request.get_json()

    if isinstance(data, list):
        results = []
        for item in data:
            cert = item.get("certificate")
            start = time.perf_counter()
            with lock:
                found = cert in cert_store
            artificial_delay()
            time_spent = (time.perf_counter() - start) * 1000
            with lock:
                total_verify_time += time_spent
            log_result("Verify", cert, time_spent, "Valid" if found else "Invalid")
            results.append({
                "certificate": cert,
                "status": "Valid" if found else "Invalid",
                "time_ms": round(time_spent, 3)
            })
        return jsonify(results)
    
    elif isinstance(data, dict):  # handle single certificate
        cert = data.get("certificate")
        start = time.perf_counter()
        with lock:
            found = cert in cert_store
        artificial_delay()
        time_spent = (time.perf_counter() - start) * 1000
        with lock:
            total_verify_time += time_spent
        log_result("Verify", cert, time_spent, "Valid" if found else "Invalid")
        return jsonify({
            "certificate": cert,
            "status": "Valid" if found else "Invalid",
            "time_ms": round(time_spent, 3)
        })

    return jsonify({"error": "Invalid input"}), 400

@app.route("/summary", methods=["GET"])
def get_summary():
    with lock:
        total_issued = len(cert_store)
        total_verified = len(cert_store)
        total_processing_time = total_issue_time + total_verify_time
        total_operations = total_verified + total_issued
        avg_time = total_processing_time / total_operations if total_operations else 0

        with open(summary_file, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                total_issued,
                total_verified,
                f"{total_issue_time:.3f}",
                f"{total_verify_time:.3f}",
                f"{total_processing_time:.3f}",
                f"{avg_time:.3f}"
            ])

    return jsonify({
        "TotalIssued": total_issued,
        "TotalVerified": total_verified,
        "TotalIssueTime_ms": round(total_issue_time, 3),
        "TotalVerifyTime_ms": round(total_verify_time, 3),
        "TotalProcessingTime_ms": round(total_processing_time, 3),
        "AverageTimePerCertificate_ms": round(avg_time, 3)
    })

if __name__ == "__main__":
    init_log_files()
    app.run(debug=True)
