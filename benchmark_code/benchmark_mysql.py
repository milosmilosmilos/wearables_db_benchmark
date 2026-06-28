import csv
import statistics
import time

import mysql.connector


CONTAINER_NAME = "mysql"
MYSQL_HOST = "localhost"
MYSQL_PORT = 3306
MYSQL_USER = "root"
MYSQL_PASSWORD = "admin"
MYSQL_DATABASE = "wearables"

TEST_RETRIES = 100
WARMUP_RUNS = 25

DATASET_LABEL = "mysql_1M"
RESULTS_FILE = f"benchmark_mysql_results_{DATASET_LABEL}.csv"

QUERIES = {
    "Q_naive_wide": """
        SELECT COUNT(*)
        FROM measurements
        WHERE heart_rate > 120
    """,
    "Q_context_wide": """
        SELECT state, COUNT(*) AS anomalies
        FROM measurements
        WHERE
            (state = 'sleeping' AND (heart_rate < 43 OR heart_rate > 73))
            OR (state = 'resting' AND (heart_rate < 54 OR heart_rate > 90))
            OR (state = 'walking' AND (heart_rate < 70 OR heart_rate > 130))
            OR (state = 'running' AND (heart_rate < 109 OR heart_rate > 181))
        GROUP BY state
    """,
    "Q_naive_narrow": """
        SELECT COUNT(*)
        FROM measurements_narrow
        WHERE sensor_type = 'heart_rate' AND value > 120
    """,
    "Q_context_narrow": """
        SELECT state, COUNT(*) AS anomalies
        FROM measurements_narrow
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


def restart_mysql():
    print(f"  -> restarting container '{CONTAINER_NAME}' ...")
    for attempt in range(30):
        try:
            conn = mysql.connector.connect(
                host=MYSQL_HOST,
                port=MYSQL_PORT,
                user=MYSQL_USER,
                password=MYSQL_PASSWORD,
                database=MYSQL_DATABASE,
                connection_timeout=2,
            )
            conn.close()
            print("  -> server ready")
            return
        except mysql.connector.Error:
            pass
        time.sleep(1)

    raise RuntimeError("MySQL serveris not up on time.")


def connect():
    conn = mysql.connector.connect(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DATABASE,
    )
    conn.autocommit = True
    return conn


def run_query_once(conn, sql):
    start = time.perf_counter()
    cursor = conn.cursor()
    cursor.execute(sql)
    cursor.fetchall()
    cursor.close()
    elapsed_ms = (time.perf_counter() - start) * 1000
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

        restart_mysql()
        conn = connect()

        latencies = []
        for i in range(TEST_RETRIES):
            elapsed = run_query_once(conn, sql)
            latencies.append(elapsed)
            print(f"  run {i + 1}/{TEST_RETRIES}: {elapsed:.2f} ms")

        conn.close()

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

    print(f"\nRezultats are in {RESULTS_FILE}")
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