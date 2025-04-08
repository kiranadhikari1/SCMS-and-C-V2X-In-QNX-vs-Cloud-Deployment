import time
import random
import csv
import concurrent.futures

# Use this to set number of certificates
MAX_CERTS = 1000
cert_store = []
log_file = "scms_report.csv"
summary_file = "scms_summary.csv"
total_issue_time = 0.0
total_verify_time = 0.0

def open_log_files():
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

def artificial_delay():
    time.sleep(0.01)  # 10 ms

def issue_certificate():
    global total_issue_time
    start = time.perf_counter()

    cert = f"CERT: {random.randint(0, 100000)}"
    cert_store.append(cert)

    artificial_delay()
    time_spent = (time.perf_counter() - start) * 1000
    total_issue_time += time_spent

    print(f"[ISSUE] Issued certificate: {cert} | Time: {time_spent:.3f} ms")
    log_result("Issue", cert, time_spent, "Issued")

def verify_certificate(cert):
    global total_verify_time
    start = time.perf_counter()

    found = cert in cert_store
    artificial_delay()
    time_spent = (time.perf_counter() - start) * 1000
    total_verify_time += time_spent

    print(f"[VERIFY] Certificate: {cert} | Status: {'VALID' if found else 'INVALID'} | Time: {time_spent:.3f} ms")
    log_result("Verify", cert, time_spent, "Valid" if found else "Invalid")

def parallel_verify(cert):
    verify_certificate(cert)

def main():
    open_log_files()
    print("\n")

    # Issue certificates
    for _ in range(MAX_CERTS):
        issue_certificate()

    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        list(executor.map(parallel_verify, cert_store))

    # Verify invalid certificate
    verify_certificate("CERT-123456")

    # Generate Summary
    total_processing_time = total_issue_time + total_verify_time
    total_operations = len(cert_store) + 1 + len(cert_store)  # issued + verified + one invalid
    average_time_per_cert = total_processing_time / total_operations

    # Write summary to file
    with open(summary_file, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([len(cert_store), len(cert_store) + 1, f"{total_issue_time:.3f}", f"{total_verify_time:.3f}", f"{total_processing_time:.3f}", f"{average_time_per_cert:.3f}"])

    print(f"\nTotal Issue Time: {total_issue_time:.3f} ms")
    print(f"Total Verify Time: {total_verify_time:.3f} ms")
    print(f"Total SCMS Processing Time: {total_processing_time:.3f} ms")
    print(f"Average Time per Certificate Operation: {average_time_per_cert:.3f} ms")

if __name__ == "__main__":
    main()

