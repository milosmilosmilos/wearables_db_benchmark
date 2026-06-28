# Impact of Database Schema Design on Contextual Anomaly Detection Performance

Accompanying code, data, and results for the seminar paper: *"Impact of Database Schema Design on the Performance of Contextual Anomaly Detection: A Case Study for Wearable Sensor Data in ClickHouse"*.

The paper empirically investigates the impact of database schema choice (wide vs. narrow) and query complexity (naive vs. contextual) on anomaly detection query latency in ClickHouse, over synthetic wearable sensor data, across five dataset sizes (1M–50M rows) and three independent repetitions per combination.

## Repository structure

```
generator_code/         Synthetic wearable dataset generator
├── config.py            Generation parameters (number of users, days, interval, anomaly rate)
├── states.py             Physiological state model and Markov chain of transitions
├── generator.py          Logic for generating a single measurement (Gaussian distribution + anomalies)
└── main.py                Entry point - runs CSV dataset generation

datasets/                Generated CSV datasets (input for ClickHouse)

benchmark_code/
└── benchmark.py          Script for automated query latency measurement (HTTP, ClickHouse)
└── benchmark_mysql.py          Script for automated query latency measurement (MySQL)

benchmark_logs/          Raw console output of individual benchmark sessions (before aggregation)

benchmark_results/       Aggregated results per test session, format:
                          benchmark_results_{size}_Run{n}.csv
                          (size ∈ {1M, 5M, 10M, 20M, 50M}, n ∈ {1, 2, 3})

generate_diagrams_code/
└── graphic.py             Generates latency and relative ratio charts (Figure 3, Figure 4)
```

## Running

1. **Data generation** – set parameters in `generator_code/config.py`, then run `main.py`. The output is a CSV dataset that is imported into ClickHouse (wide and narrow table, see the Methodology section of the paper).
2. **Benchmark** – in `benchmark_code/benchmark.py`, set `DATASET_LABEL` and ClickHouse credentials, then run. Results are saved to `benchmark_results/`.
3. **Charts** – run `generate_diagrams_code/graphic.py` to generate the final figures used in the paper.

## Requirements

- Python 3, libraries: `requests`, `matplotlib`
- Docker + ClickHouse (local instance)

## Reproducibility note

All results presented in the paper (Table 1, Table 2) are derived from the files in `benchmark_results/`, as the average of three independent medians per combination of dataset size, schema, and query type.
