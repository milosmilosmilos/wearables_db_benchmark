import csv
import statistics
import subprocess
import time

import requests


CONTAINER_NAME = "clickhouse"         
CLICKHOUSE_HTTP_URL = "http://localhost:8123/"
CLICKHOUSE_USER = "wearable"
CLICKHOUSE_PASSWORD = "wearable123" 
TEST_RETRIES = 100                     
WARMUP_RUNS = 25     

DATASET_LABEL = "50M_Run2"
RESULTS_FILE = f"benchmark_results_{DATASET_LABEL}.csv"

QUERIES = {
    "Q_naive_wide": """
        SELECT count()
        FROM wearable.measurements
        WHERE heart_rate > 120
    """,
    "Q_context_wide": """
        SELECT state, count() AS anomalies
        FROM wearable.measurements
        WHERE
            (state = 'sleeping' AND (heart_rate < 43 OR heart_rate > 73))
            OR (state = 'resting' AND (heart_rate < 54 OR heart_rate > 90))
            OR (state = 'walking' AND (heart_rate < 70 OR heart_rate > 130))
            OR (state = 'running' AND (heart_rate < 109 OR heart_rate > 181))
        GROUP BY state
    """,
    "Q_naive_narrow": """
        SELECT count()
        FROM wearable.measurements_narrow
        WHERE sensor_type = 'heart_rate' AND value > 120
    """,
    "Q_context_narrow": """
        SELECT state, count() AS anomalies
        FROM wearable.measurements_narrow
        WHERE sensor_type = 'heart_rate'
          AND (
              (state = 'sleeping' AND (value < 43 OR value > 73))
              OR (state = 'resting' AND (value < 54 OR value > 90))
              OR (state = 'walking' AND (value < 70 OR value > 130))
              OR (state = 'running' AND (value < 109 OR value > 181))
          )
        GROUP BY state
    """,
}

def restart_clickhouse():
    """Docker restart."""
    print(f"  -> restarting container '{CONTAINER_NAME}' ...")
    subprocess.run(
        ["docker", "restart", CONTAINER_NAME],
        check=True,
        capture_output=True,
    )

    for attempt in range(30):
        try:
            r = requests.get(CLICKHOUSE_HTTP_URL, timeout=2)
            if r.status_code == 200:
                print("  -> Server is ready.")
                return
        except requests.exceptions.RequestException:
            pass
        time.sleep(1)

    raise RuntimeError("ClickHouse server is not up on time.")


def run_query_once(sql):
    """Running 1 query over HTTP interface & measure round-trip time in ms."""
    start = time.perf_counter()
    response = requests.post(
        CLICKHOUSE_HTTP_URL,
        data=sql.encode("utf-8"),
        auth=(CLICKHOUSE_USER, CLICKHOUSE_PASSWORD),
    )
    elapsed_ms = (time.perf_counter() - start) * 1000

    if response.status_code != 200:
        raise RuntimeError(f"ClickHouse error: {response.text}")

    return elapsed_ms


def compute_stats(latencies):
    return {
        "min": round(min(latencies), 2),
        "median": round(statistics.median(latencies), 2), 
        "mean": round(statistics.mean(latencies), 2),
        "p95": round(sorted(latencies)[int(len(latencies) * 0.95) - 1], 2),
        "max": round(max(latencies), 2),
        "stddev": round(statistics.pstdev(latencies), 2),
    }



def main():
    all_results = []

    for query_name, sql in QUERIES.items():
        print(f"\n=== Benchmarking: {query_name} ===")

        restart_clickhouse()

        latencies = []
        for i in range(TEST_RETRIES):
            elapsed = run_query_once(sql)
            latencies.append(elapsed)
            print(f"  run {i + 1}/{TEST_RETRIES}: {elapsed:.2f} ms")

        cold_latency = latencies[0]

        warm_latencies = latencies[WARMUP_RUNS:]
        if len(warm_latencies) < 2:
            raise ValueError(
                "TEST_RETRIES must be > WARMUP_RUNS."
            )

        warm_stats = compute_stats(warm_latencies)
        warm_stats["query"] = query_name
        warm_stats["regime"] = "warm"
        warm_stats["cold_latency_ms"] = round(cold_latency, 2)
        warm_stats["dataset_size"] = DATASET_LABEL

        all_results.append(warm_stats)

        print(f"  -> COLD (1. run): {cold_latency:.2f} ms")
        print(f"  -> WARM stats (run {WARMUP_RUNS + 1}-{TEST_RETRIES}): {warm_stats}")

    with open(RESULTS_FILE, "w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "dataset_size",
                "query",
                "regime",
                "cold_latency_ms",
                "min",
                "median",
                "mean",
                "p95",
                "max",
                "stddev",
            ],
        )
        writer.writeheader()
        for row in all_results:
            writer.writerow(row)

    print(f"\nResults are recored into {RESULTS_FILE}")
    print("\n=== FINAL TABLE (warm + cold reference) ===")
    print(
        f"{'Query':<22} {'Cold':>10} {'Min':>8} {'Median':>8} {'Mean':>8} "
        f"{'95%':>8} {'Max':>8} {'StdDev':>8}"
    )
    for row in all_results:
        print(
            f"{row['query']:<22} {row['cold_latency_ms']:>10} {row['min']:>8} "
            f"{row['median']:>8} {row['mean']:>8} {row['p95']:>8} {row['max']:>8} {row['stddev']:>8}"
        )


if __name__ == "__main__":
    main()
