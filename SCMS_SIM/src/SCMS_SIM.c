#define _POSIX_C_SOURCE 199309L
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define MAX_CERTS 1000

char cert_store[MAX_CERTS][50];
int cert_count = 0;

FILE *log_file;
FILE *summary_file;

double total_issue_time = 0.0;
double total_verify_time = 0.0;

void open_log_file() {
    log_file = fopen("scms_report.csv", "w");
    if (log_file == NULL) {
        printf("Error opening log file!\n");
        exit(1);
    }
    fprintf(log_file, "Operation,Certificate,ProcessingTime(ms),Status\n");

    summary_file = fopen("scms_summary.csv", "w");
    if (summary_file == NULL) {
        printf("Error opening summary file!\n");
        exit(1);
    }
    fprintf(summary_file, "TotalIssued,TotalVerified,TotalIssueTime(ms),TotalVerifyTime(ms),TotalProcessingTime(ms),AverageTimePerCertificate(ms)\n");
}

void close_log_file() {
    fclose(log_file);
    fclose(summary_file);
}

void log_result(const char *operation, const char *cert, double time, const char *status) {
    fprintf(log_file, "%s,%s,%.3f,%s\n", operation, cert, time, status);
}

void artificial_delay() {
    struct timespec delay = {0, 10000000L};  // 10 ms
    nanosleep(&delay, NULL);
}

void issue_certificate() {
    struct timespec start, end;
    clock_gettime(CLOCK_REALTIME, &start);

    char cert[50];
    sprintf(cert, "CERT: %d", rand() % 100000);

    strcpy(cert_store[cert_count], cert);
    cert_count++;

    artificial_delay();

    clock_gettime(CLOCK_REALTIME, &end);
    double time_spent = (end.tv_sec - start.tv_sec) * 1e3 + (end.tv_nsec - start.tv_nsec) / 1e6;
    total_issue_time += time_spent;

    printf("[ISSUE] Issued certificate: %s | Time: %.3f ms\n", cert, time_spent);
    log_result("Issue", cert, time_spent, "Issued");
}

void verify_certificate(const char *cert) {
    struct timespec start, end;
    clock_gettime(CLOCK_REALTIME, &start);

    int found = 0;
    for (int i = 0; i < cert_count; i++) {
        if (strcmp(cert_store[i], cert) == 0) {
            found = 1;
            break;
        }
    }

    artificial_delay();
    clock_gettime(CLOCK_REALTIME, &end);
    double time_spent = (end.tv_sec - start.tv_sec) * 1e3 + (end.tv_nsec - start.tv_nsec) / 1e6;
    total_verify_time += time_spent;

    printf("[VERIFY] Certificate: %s | Status: %s | Time: %.3f ms\n",
           cert, found ? "VALID" : "INVALID", time_spent);
    log_result("Verify", cert, time_spent, found ? "Valid" : "Invalid");
}

int main() {
    srand(time(NULL));
    open_log_file();

    // Issue certificates
    for (int i = 0; i < 1000; i++) {
        issue_certificate();
    }

    printf("\n");

    // Verify certificates
    for (int i = 0; i < cert_count; i++) {
        verify_certificate(cert_store[i]);
    }

    // Verify invalid certificate
    verify_certificate("CERT-123456");  // Invalid

    // Summary
    double total_processing_time = total_issue_time + total_verify_time;
    int total_operations = cert_count + 1 + cert_count; // all issued + one invalid that was added
    double average_time_per_cert = total_processing_time / total_operations;

    fprintf(summary_file, "%d,%d,%.3f,%.3f,%.3f,%.3f\n",
            cert_count, cert_count + 1, total_issue_time, total_verify_time, total_processing_time, average_time_per_cert);

    printf("\nTotal Issue Time: %.3f ms\n", total_issue_time);
    printf("Total Verify Time: %.3f ms\n", total_verify_time);
    printf("Total SCMS Processing Time: %.3f ms\n", total_processing_time);
    printf("Average Time per Certificate Operation: %.3f ms\n", average_time_per_cert);

    close_log_file();
    return 0;
}
