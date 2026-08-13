# Benchmark Methodology

## 1. Objective

This project benchmarks graph database performance under a controlled
resource envelope using the same canonical dataset and equivalent logical
workloads across all supported databases.

The benchmark currently evaluates:

- CognoDB
- Neo4j
- Memgraph
- FalkorDB
- ArcadeDB

The benchmark measures two primary areas:

1. Data ingestion performance
2. Query execution performance

The objective is to provide a reproducible and transparent comparison of
graph database performance for the selected dataset and workload suite.

The results should be interpreted as performance measurements for the
documented environment and configuration rather than as a universal ranking
of graph databases.

---

## 2. Resource Envelope

All databases are benchmarked using the same target resource envelope
wherever the deployment model permits.

| Resource | Target |
|---|---:|
| CPU | 0.5 vCPU |
| Memory | 512 MB |
| Storage | 1 GB |

The CognoDB Cloud free tier currently provides 512 MB RAM, burstable to
0.5 vCPU, with 1 GiB storage.

The assignment describes the CognoDB free tier as 256 MB RAM. However, the
currently available CognoDB c0 configuration provides 512 MB RAM and no
256 MB configuration was available.

Therefore, the benchmark uses the currently available c0 configuration and
constrains all self-hosted databases to the same 512 MB / 0.5 CPU envelope.

Database-specific configuration required for successful operation within
this resource envelope is documented rather than silently relying on
unrestricted defaults.

---

## 3. Database Versions and Deployment

The benchmark uses the following database versions and deployment models:

| Database | Version | Deployment |
|---|---|---|
| CognoDB | 0.9.11 | Cloud |
| Neo4j | 5.26.29 | Docker |
| Memgraph | 3.12.0 | Docker |
| FalkorDB | 4.20.1 | Docker |
| ArcadeDB | 26.7.3 | Docker |

Database version and deployment information are considered part of the
benchmark environment.

Results should therefore be associated with the database versions and
configuration used to produce them.

---

## 4. Dataset

Every database is benchmarked using the same canonical processed dataset.

The dataset contains:

- **36,692 nodes**
- **183,831 relationships**

The processed node dataset is:

```text
data/processed/nodes.csv
```

The processed relationship dataset is:

```text
data/processed/relationships.csv
```

The expected dataset size is:

```text
Nodes:         36,692
Relationships: 183,831
```

The benchmark validates the number of records loaded into the database
before query benchmarking begins.

If the actual node count or relationship count differs from the configured
expected values, the benchmark fails rather than continuing with an
inconsistent dataset.

This prevents incomplete or incorrect ingestion from affecting query
performance measurements.

---

## 5. Graph Data Model

The benchmark uses a common logical graph model across all supported
databases.

Users are represented as nodes:

```text
(:User {id: <integer>})
```

Relationships are represented as directed `KNOWS` relationships:

```text
(:User)-[:KNOWS]->(:User)
```

The physical representation may differ between databases, but the logical
dataset and workload semantics remain consistent.

---

## 6. Database Adapter Architecture

Each supported database implements the common:

```text
GraphDatabaseAdapter
```

interface.

The adapter provides the following operations:

- `connect()`
- `close()`
- `execute()`
- `clear()`
- `health_check()`
- `load_nodes()`
- `load_relationships()`
- `count_nodes()`
- `count_relationships()`

The benchmark runner operates against this common interface.

Database-specific connection, ingestion, query execution, and cleanup
behavior remains inside the corresponding adapter.

This allows the benchmark lifecycle to remain database-independent while
still allowing each database to use its appropriate driver and query syntax.

---

## 7. Ingestion Methodology

Each benchmark run begins by loading the canonical dataset into the target
database.

The ingestion lifecycle is:

1. Establish a database connection.
2. Load all nodes.
3. Load all relationships.
4. Measure total ingestion time.
5. Validate node count.
6. Validate relationship count.
7. Begin query benchmarking.

The default ingestion batch size is:

```text
1,000 records
```

The benchmark records:

- Number of nodes loaded
- Number of relationships loaded
- Total ingestion time
- Nodes per second
- Relationships per second

The node and relationship counts are validated against the expected dataset
counts before query execution.

---

## 8. Benchmark Workloads

The benchmark currently defines seven logical workloads:

| Workload | Description |
|---|---|
| `point_lookup` | Lookup a single user by ID |
| `indexed_lookup` | Lookup a user through an indexed lookup path |
| `relationship_lookup` | Find direct `KNOWS` relationships |
| `traversal_1_hop` | Traverse exactly one `KNOWS` hop |
| `traversal_2_hop` | Traverse exactly two `KNOWS` hops |
| `traversal_3_hop` | Traverse exactly three `KNOWS` hops |
| `aggregation` | Count all users |

All five supported databases expose the same logical workload set through
the workload registry.

The actual query syntax is database-specific where required.

This allows the benchmark to compare equivalent logical operations without
requiring every database to execute an identical query string.

---

## 9. Point Lookup

The point lookup workload retrieves a user by ID.

Logical operation:

```text
Find User where id = X
```

The workload is parameterized using a deterministic node ID generated from
the configured query seed.

---

## 10. Indexed Lookup

The indexed lookup workload measures lookup performance through the
database's indexed access path.

Logical operation:

```text
Find the User with a specific ID using an indexed lookup path.
```

The exact implementation depends on the database's supported indexing and
query capabilities.

The benchmark keeps the logical operation consistent while allowing
database-specific query syntax.

---

## 11. Relationship Lookup

The relationship lookup workload retrieves direct `KNOWS` relationships
from a selected user.

Logical operation:

```text
User -> direct KNOWS relationships
```

This measures basic relationship expansion from a known starting node.

---

## 12. Traversal Workloads

Traversal is divided into three independent workloads:

```text
traversal_1_hop
traversal_2_hop
traversal_3_hop
```

They represent:

```text
1 hop:
User -> User

2 hops:
User -> User -> User

3 hops:
User -> User -> User -> User
```

Each traversal workload measures an exact traversal depth rather than using
one variable-depth workload.

This allows performance behavior at different traversal depths to be
observed independently.

---

## 13. Traversal Result Limit

Traversal workloads use a bounded result limit of:

```text
1,000 rows
```

The limit is applied to the traversal workloads across the supported
databases.

The purpose of the bound is to prevent highly connected nodes from
producing excessively large result sets that could:

- dominate execution time,
- consume excessive resources,
- exceed server-side row budgets, or
- make comparisons between databases impractical.

The result limit therefore defines the benchmark operation as a bounded
traversal rather than an unrestricted result-materialization test.

---

## 14. Aggregation

The aggregation workload counts all `User` nodes in the graph.

Logical operation:

```text
Count all User nodes
```

This workload represents a graph-wide aggregation operation and differs
from point lookups and traversal workloads because it operates over the
entire node population.

---

## 15. Query Parameter Generation

Workloads that require a node ID use deterministic node IDs.

The default query seed is:

```text
42
```

Node IDs are generated using a seeded pseudo-random number generator.

For the same:

- dataset size,
- query seed,
- warmup iteration count, and
- measurement iteration count,

the benchmark generates the same sequence of node IDs.

This ensures that comparable database runs use the same logical sequence of
query parameters.

The deterministic sequence also makes benchmark runs easier to reproduce
and debug.

---

## 16. Warmup Phase

Each workload has a warmup phase before measurements begin.

The default warmup configuration is:

```text
10 iterations
```

Warmup executions are excluded from the reported measurements.

The purpose of warmup is to allow the database and client runtime to reach a
more stable execution state before latency measurements are collected.

The number of warmup iterations can be overridden through the CLI.

Example:

```powershell
python -m benchmark.cli --database MEMGRAPH --iterations 100 --warmup 10
```

---

## 17. Measurement Phase

After warmup, the benchmark executes the configured number of measured
iterations.

The default measurement configuration is:

```text
100 iterations
```

Each iteration executes the workload once and records its execution
latency.

The measurement phase excludes warmup executions.

---

## 18. Query Latency Measurement

Each measured query execution is timed independently using a high-resolution
monotonic timer.

The benchmark records individual latency observations and derives:

- Minimum latency
- Maximum latency
- Mean latency
- P50 latency
- P95 latency
- P99 latency
- Queries per second (QPS)

Latency is measured internally in seconds and converted to milliseconds for
human-readable benchmark reporting.

---

## 19. Latency Percentiles

### P50

P50 represents the median observed query latency.

It describes typical query execution behavior.

### P95

P95 represents the latency at which approximately 95% of measured
executions are at or below the reported value.

P95 is used as the primary query latency metric for normalized scoring
because it captures tail behavior more effectively than the mean alone.

### P99

P99 represents the latency at which approximately 99% of measured
executions are at or below the reported value.

P99 provides additional visibility into high-latency observations.

---

## 20. Queries Per Second

Query throughput is reported as queries per second:

```text
QPS = measured iterations / total measurement time
```

Only the measurement phase is included in this calculation.

Warmup executions are excluded.

Higher QPS represents higher query throughput.

---

## 21. Benchmark Run Lifecycle

A benchmark run follows this general lifecycle:

```text
Create run metadata
        |
        v
Create run directory
        |
        v
Connect to database
        |
        v
Load nodes
        |
        v
Load relationships
        |
        v
Validate dataset counts
        |
        v
Warm up workloads
        |
        v
Measure workloads
        |
        v
Write raw results
        |
        v
Clear benchmark data
        |
        v
Close database connection
```

Database cleanup and connection closure occur after the benchmark run.

This prevents benchmark data from accumulating across independent runs.

---

## 22. Run IDs and Run Directories

Every benchmark execution receives a UTC-based run ID.

Example:

```text
20260812T204838Z
```

Results for an individual run are stored under:

```text
results/runs/<run_id>/
```

For example:

```text
results/
└── runs/
    └── 20260812T204838Z/
        ├── metadata.json
        └── memgraph.json
```

This keeps individual benchmark executions isolated and traceable.

---

## 23. Run Metadata

Each benchmark run records environment and configuration metadata.

The metadata includes:

- Run ID
- UTC timestamp
- Git commit
- Python version
- Platform
- Processor
- Node count
- Relationship count
- Ingestion batch size
- Query iteration count
- Query warmup iteration count
- Query seed

Example:

```json
{
  "run_id": "20260812T204838Z",
  "timestamp_utc": "2026-08-12T20:48:38.215980+00:00",
  "git_commit": "13df07ff5c9c869a3198946c9537a0f225d3f2ec",
  "python_version": "3.13.14",
  "platform": "Windows-11-10.0.26200-SP0",
  "processor": "Intel64 Family 6 Model 186 Stepping 2, GenuineIntel",
  "node_count": 36692,
  "relationship_count": 183831,
  "ingestion_batch_size": 1000,
  "query_iterations": 100,
  "query_warmup_iterations": 10,
  "query_seed": 42
}
```

The Git commit is particularly important because it associates a benchmark
result with the source-code revision that produced it.

---

## 24. Database-Specific Workload Definitions

The benchmark separates logical workload definitions from database-specific
query syntax.

The workload registry associates every database with its corresponding
workload definitions.

The supported databases are:

```text
NEO4J
MEMGRAPH
FALKORDB
ARCADEDB
COGNODB
```

Each registry entry provides:

```text
point_lookup
indexed_lookup
relationship_lookup
traversal_1_hop
traversal_2_hop
traversal_3_hop
aggregation
```

This ensures that the benchmark runner does not need to contain
database-specific query logic.

---

## 25. Database Query Languages

The benchmark allows each database to use its supported query language or
compatible interface.

Examples include:

- Neo4j: Cypher
- Memgraph: Cypher-compatible graph queries
- FalkorDB: supported graph query interface
- CognoDB: Neo4j-compatible Bolt interface
- ArcadeDB: ArcadeDB SQL/graph traversal syntax

The benchmark compares the logical operation represented by each workload,
not the textual similarity of the query implementations.

---

## 26. Preflight Verification

Before benchmark execution, each database was verified under the target
resource envelope.

The preflight verification included:

1. Database startup verification
2. Connectivity verification
3. Simple query execution
4. Node/vertex creation
5. Basic lookup verification
6. Basic count verification

All five databases successfully passed the preflight verification.

---

## 27. Neo4j Memory Configuration

Neo4j required explicit JVM memory configuration to operate within the
512 MB container limit.

The preflight configuration used:

- Container memory: 512 MB
- Container CPU: 0.5 vCPU
- JVM heap maximum: 256 MB
- Page cache: 128 MB

Neo4j successfully started and passed functional queries without being
OOM-killed under the tested configuration.

---

## 28. CognoDB Compatibility

CognoDB is accessed through its Neo4j-compatible Bolt interface.

The benchmark uses the Neo4j Python driver for the CognoDB adapter.

CognoDB therefore uses the same logical graph model and parameterized query
execution model while maintaining its own database adapter.

Traversal workloads were specifically validated against CognoDB because
highly connected nodes in the dataset can produce large intermediate result
sets.

During validation, unrestricted traversal could exceed the server-side row
budget.

The final traversal workloads therefore use the common 1,000-row result
bound.

This keeps the workload bounded and prevents a database-specific server
row-limit failure from invalidating the benchmark run.

---

## 29. Result Files

Individual benchmark runs produce raw structured JSON results.

The broader benchmark pipeline also produces derived artifacts.

The main result directory contains:

```text
results/
├── comparison.json
├── comparison.csv
├── rankings.json
├── scores.json
├── statistics.json
├── tail_analysis.json
└── plots/
```

Individual run results are stored under:

```text
results/runs/
└── <run_id>/
    ├── metadata.json
    └── <database>.json
```

The separation between raw runs and derived results allows analysis to be
performed without modifying the original benchmark observations.

---

## 30. Comparison

The comparison stage combines benchmark results from the supported
databases.

It provides a common representation of:

- Ingestion performance
- Query latency
- Query throughput
- Workload-level results

The comparison output can be exported as both JSON and CSV.

---

## 31. Normalized Scoring

The scoring pipeline uses best-value normalization.

For metrics where lower values are better:

```text
score = best_value / database_value
```

For metrics where higher values are better:

```text
score = database_value / best_value
```

The best-performing database for an individual metric therefore receives:

```text
1.0
```

Other databases receive a normalized score relative to the best observed
value.

The primary query latency metric used by the scoring system is:

```text
P95 latency
```

---

## 32. Ingestion Scoring

Ingestion scoring considers ingestion elapsed time as the primary
normalized ingestion metric.

Lower ingestion time is better.

The ingestion score is therefore calculated using lower-is-better
normalization.

The benchmark also records:

- Nodes per second
- Relationships per second

These throughput metrics are normalized using higher-is-better
normalization when included in the scoring data.

---

## 33. Query Scoring

Every workload receives two normalized query scores:

1. P95 latency score
2. QPS score

For each workload:

```text
workload_score =
    (latency_score * 0.5)
    + (qps_score * 0.5)
```

Therefore:

```text
50% P95 latency
50% QPS
```

Each workload contributes equally to the aggregate query score.

---

## 34. Overall Score

The overall benchmark score uses:

```text
20% ingestion performance
80% query performance
```

The calculation is:

```text
overall_score =
    (ingestion_score * 0.20)
    + (query_score * 0.80)
```

The query score is the average workload score across all workloads included
in the comparison.

The current workload suite therefore gives equal weight to:

- `point_lookup`
- `indexed_lookup`
- `relationship_lookup`
- `traversal_1_hop`
- `traversal_2_hop`
- `traversal_3_hop`
- `aggregation`

The overall score is a project-specific comparison metric and should not be
interpreted as an absolute measure of database quality.

---

## 35. Fairness Considerations

The benchmark attempts to keep the following factors consistent across
databases:

- Canonical dataset
- Dataset size
- Logical workload definitions
- Query parameter sequence
- Query seed
- Warmup methodology
- Measurement methodology
- Query iteration count
- Ingestion batch size
- Target CPU envelope
- Target memory envelope

Where database-specific configuration is required for successful operation,
that configuration is documented rather than hidden.

The benchmark therefore aims for controlled comparison rather than forcing
identical internal database configuration where that would be technically
inappropriate.

---

## 36. Reproducibility

A reproducible benchmark should use the same:

1. Dataset
2. Database versions
3. Deployment model
4. Resource envelope
5. Database configuration
6. Ingestion batch size
7. Query iteration count
8. Warmup iteration count
9. Query seed
10. Workload definitions
11. Benchmark source-code revision

Run metadata records the benchmark configuration and execution environment
needed to trace a result back to its source.

The Git commit recorded in `metadata.json` provides an explicit link between
a benchmark result and the benchmark implementation that produced it.

---

## 37. Benchmark Limitations

The benchmark should be interpreted within its documented scope.

Results can vary due to:

- Hardware differences
- CPU scheduling
- Memory pressure
- Storage performance
- Network latency
- Cloud service behavior
- Database version
- Runtime configuration
- JVM configuration
- Query planner behavior
- Database-specific indexing
- Dataset structure
- Dataset distribution
- Cache state
- Background database activity

The benchmark uses a single canonical dataset and a fixed workload suite.
Therefore, results may not represent workloads or datasets outside this
benchmark.

The overall score is also dependent on the chosen weighting methodology:

```text
20% ingestion
80% queries
```

and:

```text
50% P95 latency
50% QPS
```

Changing these weights can change the resulting ranking.

---

## 38. Interpretation

The benchmark is intended to answer questions such as:

- How quickly can each database ingest the canonical dataset?
- How does point lookup performance compare?
- How does indexed lookup performance compare?
- How does relationship lookup performance compare?
- How does performance change as traversal depth increases?
- How does graph-wide aggregation performance compare?
- How does tail latency differ between databases?
- How does query throughput differ under the same benchmark configuration?

It should not be interpreted as:

- a universal ranking of graph databases,
- a replacement for production workload testing,
- a comprehensive evaluation of database features,
- or a guarantee of production performance.

The results represent the behavior of the tested database versions under
the documented environment, dataset, workloads, and configuration.

---

## 39. Methodology Summary

The complete benchmark methodology can be summarized as:

```text
Same dataset
     |
     v
Same logical graph model
     |
     v
Same resource envelope
     |
     v
Same workload suite
     |
     v
Same deterministic query sequence
     |
     v
Same warmup/measurement methodology
     |
     v
Latency + QPS + ingestion measurements
     |
     v
Raw benchmark results
     |
     v
Statistics and comparison
     |
     v
Normalized scoring
     |
     v
Visualization and analysis
```

The methodology is designed to make benchmark execution measurable,
repeatable, and auditable while clearly documenting the assumptions and
limitations behind the resulting performance comparisons.