# Results and Scoring

## 1. Purpose

This document explains how benchmark execution results are stored, compared, normalized, and converted into the final benchmark scores.

The scoring system is implemented in:

```text
benchmark/scoring.py
```

The comparison data used by the scorer is produced by the benchmark result/comparison pipeline.

The scoring system is intended to provide a consistent relative comparison of the supported databases under the documented benchmark environment.

A score is not an absolute measure of database quality. It is a normalized performance indicator relative to the other databases included in the same benchmark run.

---

## 2. Result Artifacts

Benchmark execution produces run-specific result directories under:

```text
results/runs/
```

A typical run has the following structure:

```text
results/
└── runs/
    └── <run_id>/
        ├── metadata.json
        ├── neo4j.json
        ├── memgraph.json
        ├── falkordb.json
        ├── arcadedb.json
        └── cognodb.json
```

The exact database result files present depend on which databases were executed.

Additional aggregate artifacts are stored directly under `results/`:

```text
results/
├── comparison.json
└── scores.json
```

---

## 3. Run Metadata

Each benchmark run records metadata describing the environment and benchmark configuration.

A typical `metadata.json` contains:

```json
{
  "run_id": "...",
  "timestamp_utc": "...",
  "git_commit": "...",
  "python_version": "...",
  "platform": "...",
  "processor": "...",
  "node_count": 36692,
  "relationship_count": 183831,
  "ingestion_batch_size": 1000,
  "query_iterations": 100,
  "query_warmup_iterations": 10,
  "query_seed": 42
}
```

The metadata makes an individual result traceable to:

- the benchmark run
- the source Git revision
- the Python runtime
- the operating environment
- the processor
- the dataset size
- ingestion configuration
- query iteration configuration
- deterministic query selection

This information is important when reproducing or comparing benchmark runs.

---

## 4. Raw Database Results

Each database result records the measurements produced for that database.

The result model contains two major categories:

```text
Ingestion
Queries
```

### Ingestion

The ingestion result records:

- node count
- relationship count
- elapsed time
- nodes per second
- relationships per second

### Queries

Each workload records:

- database
- workload name
- number of iterations
- warmup iterations
- total measurement time
- individual query latencies
- calculated latency statistics
- QPS

The individual latency measurements are retained so that summary statistics can be derived from the actual measurements.

---

## 5. Ingestion Metrics

### 5.1 Elapsed Time

Ingestion elapsed time is the total time required to load the benchmark dataset.

The metric is expressed in seconds.

Lower values are better.

---

### 5.2 Nodes per Second

Nodes per second is calculated from the number of loaded nodes and the ingestion duration.

Conceptually:

```text
nodes_per_second = node_count / elapsed_seconds
```

Higher values are better.

---

### 5.3 Relationships per Second

Relationships per second represents relationship ingestion throughput.

Conceptually:

```text
relationships_per_second = relationship_count / elapsed_seconds
```

Higher values are better.

---

## 6. Query Metrics

For every workload, the benchmark records individual execution latencies.

The following statistics are calculated.

### Minimum

The fastest measured query execution.

### Mean

The arithmetic mean of all measured query latencies.

### P50

The 50th percentile, representing median latency.

### P95

The 95th percentile.

This represents the latency below which approximately 95% of measured executions fall.

### P99

The 99th percentile.

This captures more extreme tail behavior than P95.

### Maximum

The slowest measured execution.

### QPS

Queries per second represents measured query throughput.

Conceptually:

```text
QPS = iterations / total_measurement_time
```

Higher QPS is better.

---

## 7. Primary Query Latency Metric

The scoring system uses:

```text
p95_ms
```

as the primary query latency metric.

The reason is that P95 captures tail behavior better than the mean.

A database may have a good average latency while still producing significantly slower requests under part of the workload.

Using P95 makes those slower executions visible in the normalized comparison.

---

## 8. Comparison Data

The scoring pipeline consumes the comparison result:

```text
results/comparison.json
```

The comparison contains the benchmark measurements organized by database and workload.

The scorer does not maintain a second hard-coded workload list.

Instead, workloads are taken directly from:

```text
comparison["queries"]
```

This keeps scoring aligned with the workloads actually present in the comparison result.

---

## 9. Normalization

Raw benchmark measurements have different units and directions.

For example:

- latency is measured in milliseconds and lower is better
- QPS is measured as throughput and higher is better
- ingestion time is measured in seconds and lower is better
- ingestion throughput is measured in nodes/sec or relationships/sec and higher is better

The scorer therefore converts raw values into normalized scores.

The normalization method is:

```text
best_value_normalization
```

The best database receives:

```text
1.0
```

Other databases receive a value between zero and one based on their relative performance.

---

## 10. Lower-Is-Better Normalization

For metrics where lower values are better, the scorer uses:

```text
score = best_value / database_value
```

where:

```text
best_value = minimum value among all databases
```

This is used for:

- ingestion elapsed time
- query P95 latency

### Example

If the best P95 latency is:

```text
10 ms
```

and another database has:

```text
20 ms
```

then:

```text
score = 10 / 20
      = 0.5
```

The best database receives:

```text
10 / 10 = 1.0
```

---

## 11. Higher-Is-Better Normalization

For metrics where higher values are better, the scorer uses:

```text
score = database_value / best_value
```

where:

```text
best_value = maximum value among all databases
```

This is used for:

- nodes/sec
- relationships/sec
- QPS

### Example

If the best QPS is:

```text
1000
```

and another database achieves:

```text
500
```

then:

```text
score = 500 / 1000
      = 0.5
```

The best database receives:

```text
1000 / 1000 = 1.0
```

---

## 12. Ingestion Score

The overall ingestion component uses normalized ingestion elapsed time.

The benchmark gives ingestion a weight of:

```text
20%
```

The ingestion score used in the final overall score is the normalized elapsed-time score.

Nodes/sec and relationships/sec are also calculated and retained in the scoring output as normalized ingestion metrics.

This provides additional visibility into ingestion throughput without introducing additional weights into the overall score.

---

## 13. Query Workload Scores

Every workload receives a workload score composed of:

```text
50% P95 latency
50% QPS
```

For a database and workload:

```text
workload_score =
    (latency_score * 0.5)
    + (qps_score * 0.5)
```

The latency component uses lower-is-better normalization.

The QPS component uses higher-is-better normalization.

---

## 14. Query Performance Score

The query performance score is the arithmetic average of the workload scores.

Conceptually:

```text
query_score =
    sum(workload_scores) / number_of_workloads
```

All workloads present in the comparison receive equal weight.

The current workload suite contains:

```text
point_lookup
indexed_lookup
relationship_lookup
traversal_1_hop
traversal_2_hop
traversal_3_hop
aggregation
```

Therefore, each workload contributes equally to the query-performance component.

---

## 15. Overall Score

The final overall score uses:

```text
20% ingestion
80% query performance
```

The formula is:

```text
overall_score =
    ingestion_score * 0.20
    + query_score * 0.80
```

This intentionally gives query execution performance greater influence than ingestion performance.

The benchmark is primarily concerned with graph query behavior, while ingestion remains an important secondary performance characteristic.

---

## 16. Score Interpretation

A normalized score should be interpreted relative to the best database in the same benchmark comparison.

### Score = 1.0

The database is the best performer for that metric according to the normalization rule.

### Score = 0.5

The database achieved approximately half the normalized performance of the best database for that metric.

For lower-is-better metrics, this corresponds to approximately twice the best measured value.

### Score close to 0

The database performed substantially worse than the best database for that metric.

The score does not mean that the database is inherently poor or unusable.

It only describes its relative performance under the benchmark conditions.

---

## 17. Ranking

Databases are ranked by:

```text
overall_score
```

in descending order.

The database with the highest overall score is ranked first.

The ranking is therefore a relative ranking produced from:

```text
20% ingestion
80% query performance
```

with query workloads equally weighted and each workload split equally between P95 latency and QPS.

---

## 18. Example Score Structure

The generated `results/scores.json` follows the general structure:

```json
{
  "databases": [
    "neo4j",
    "memgraph",
    "falkordb",
    "arcadedb",
    "cognodb"
  ],
  "methodology": {
    "query_latency_metric": "p95_ms",
    "normalization": "best_value_normalization"
  },
  "ingestion": {},
  "queries": {},
  "overall": {}
}
```

The `overall` section contains:

```text
ingestion_score
query_score
overall_score
```

for every database.

The query section contains normalized:

```text
latency
qps
```

scores for each workload.

---

## 19. Why Normalization Is Used

Raw values cannot be combined directly because the metrics have different units and performance directions.

For example:

```text
ingestion time → seconds
P95 latency    → milliseconds
QPS            → queries/second
```

Normalization converts these measurements into a common relative scale.

The scale is anchored to the best measured value for each metric.

This makes it possible to combine multiple performance dimensions into a single overall score while preserving the direction of each metric.

---

## 20. Important Scoring Limitation

The overall score is a benchmark-specific composite score.

Changing any of the following can change the ranking:

- resource allocation
- database version
- dataset
- workload suite
- workload weights
- ingestion/query weights
- latency metric
- query iteration count
- warmup count
- database configuration

Therefore, the overall ranking should not be interpreted as a universal ranking of graph databases.

It is a ranking for the documented benchmark configuration.

---

## 21. Reproducibility

A benchmark result should be interpreted together with its metadata.

At minimum, a reproducible run should preserve:

```text
Git commit
Python version
Platform
Processor
Dataset node count
Dataset relationship count
Ingestion batch size
Query iterations
Warmup iterations
Query seed
Database versions
Deployment configuration
Resource envelope
```

The benchmark records many of these values automatically in `metadata.json`.

The remaining environment-specific details are documented in the benchmark methodology and deployment configuration.

---

## 22. Comparing Multiple Runs

When comparing two benchmark runs, the runs should use the same:

1. dataset
2. database versions
3. resource envelope
4. workload definitions
5. query seed
6. iteration counts
7. warmup configuration
8. database configuration
9. benchmark source revision where appropriate

If these conditions differ, the results should not be treated as a direct controlled comparison.

A change in benchmark configuration can affect the measurements independently of the database implementation being evaluated.

---

## 23. Result Interpretation

A benchmark result should be read in layers rather than relying only on the final ranking.

Recommended interpretation order:

```text
Raw measurements
      ↓
Latency and throughput statistics
      ↓
Per-workload comparison
      ↓
Normalized metric scores
      ↓
Query performance score
      ↓
Overall score
```

The raw measurements provide the underlying evidence.

The normalized scores provide relative comparison.

The overall score provides a compact summary.

---

## 24. Limitations

The benchmark does not attempt to measure every characteristic of a graph database.

It focuses on the selected:

- dataset
- resource envelope
- ingestion workload
- query workload suite
- database versions
- deployment configurations

It does not by itself establish:

- universal database superiority
- production reliability
- operational cost
- ecosystem quality
- developer experience
- feature completeness
- distributed scaling behavior
- failure recovery behavior
- security posture
- long-running workload behavior

Those characteristics require separate evaluation.

---

## 25. Recommended Reporting

When publishing benchmark results, report the following together:

### Environment

- database version
- deployment model
- CPU
- memory
- storage
- operating environment

### Dataset

- node count
- relationship count

### Workload configuration

- workload names
- query seed
- warmup iterations
- measurement iterations
- traversal result limit

### Raw performance

- ingestion time
- nodes/sec
- relationships/sec
- P50
- P95
- P99
- QPS

### Derived results

- normalized scores
- query score
- ingestion score
- overall score
- ranking

This prevents the final ranking from being separated from the measurements and assumptions that produced it.

---

## 26. Summary

The benchmark scoring pipeline follows this model:

```text
Raw benchmark results
        |
        v
Comparison data
        |
        +----------------------+
        |                      |
        v                      v
Ingestion metrics       Query metrics
        |                      |
        v                      v
Normalization           P95 + QPS normalization
        |                      |
        |                      v
        |               Per-workload scores
        |                      |
        |                      v
        |               Query performance score
        |                      |
        +----------+-----------+
                   |
                   v
            Overall score
          20% ingestion
          80% queries
```

The resulting score is a controlled, relative measurement of performance for the benchmark environment and should always be interpreted together with the methodology, workload definitions, raw measurements, and recorded run metadata.
