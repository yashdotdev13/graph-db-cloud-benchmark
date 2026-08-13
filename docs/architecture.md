# Benchmark Architecture

## 1. Overview

The project is structured as a modular benchmarking framework that separates:

- database connectivity
- dataset ingestion
- workload definition
- query execution
- benchmark orchestration
- result collection
- statistical analysis
- comparison
- scoring
- visualization
- run metadata and reproducibility

The architecture allows multiple graph databases to be evaluated through a common benchmark interface while keeping database-specific connection and query details isolated.

---

## 2. High-Level Architecture

```text
Benchmark CLI
     |
     v
Benchmark Runner
     |
     +--------------------+
     |                    |
     v                    v
Database Registry    Workload Registry
     |                    |
     v                    v
Database Adapters    Workload Definitions
     |                    |
     +---------+----------+
               |
               v
       Canonical Dataset
               |
               v
        Benchmark Results
               |
        +------+------+
        |             |
        v             v
 Comparison/Stats  Scoring
        |             |
        +------+------+
               |
               v
       Analysis / Reports
```

---

## 3. Database Adapter Abstraction

All supported databases implement the common `GraphDatabaseAdapter` interface defined in:

```text
databases/base.py
```

The adapter interface provides a consistent contract for:

- connecting to the database
- closing the connection
- executing queries
- clearing benchmark data
- health checking
- loading nodes
- loading relationships
- counting nodes
- counting relationships
- reporting the canonical database name

Database-specific behavior remains inside:

```text
databases/
├── base.py
├── neo4j.py
├── memgraph.py
├── falkordb.py
├── arcadedb.py
└── cognodb.py
```

---

## 4. Database Registry

Database creation is centralized in:

```text
benchmark/database_registry.py
```

The registry maps logical database names to their adapter implementations:

```text
NEO4J     -> Neo4jAdapter
MEMGRAPH  -> MemgraphAdapter
FALKORDB  -> FalkorDBAdapter
ARCADEDB  -> ArcadeDBAdapter
COGNODB   -> CognoDBAdapter
```

Connection settings are loaded through:

```text
config/settings.py
```

This keeps credentials and connection endpoints outside the benchmark implementation.

---

## 5. Workload Registry

Benchmark workloads are represented by the immutable `BenchmarkWorkload` model:

```text
benchmark/workload.py
```

Each workload contains:

- name
- description
- query
- optional parameters
- optional result limit

The workload registry is:

```text
benchmark/workload_registry.py
```

Equivalent logical operations can use database-specific query syntax while retaining the same benchmark semantics.

Current query-language mapping is:

```text
Neo4j / Memgraph / FalkorDB / CognoDB
        -> Cypher

ArcadeDB
        -> ArcadeDB SQL / traversal syntax
```

---

## 6. Workload Suite

The benchmark currently evaluates:

- `point_lookup`
- `indexed_lookup`
- `relationship_lookup`
- `traversal_1_hop`
- `traversal_2_hop`
- `traversal_3_hop`
- `aggregation`

### Point Lookup

Find a single user by ID.

### Indexed Lookup

Execute the indexed lookup workload using the benchmark's indexed access path.

### Relationship Lookup

Find direct `KNOWS` relationships from a user.

### Traversal Workloads

Traverse exactly one, two, or three `KNOWS` hops.

Traversal workloads use a bounded result limit of 1000 rows to prevent pathological high-degree traversal results from exceeding database/server result budgets.

### Aggregation

Count all benchmark users.

---

## 7. Canonical Dataset

All databases use the same processed dataset:

```text
data/processed/nodes.csv
data/processed/relationships.csv
```

The benchmark dataset contains:

```text
Nodes:          36,692
Relationships: 183,831
```

Dataset counting and validation are handled by:

```text
benchmark/dataset.py
```

The benchmark runner validates the actual ingested counts against the configured expected counts before query benchmarking begins.

---

## 8. Benchmark Execution Flow

A benchmark run follows this sequence:

```text
CLI
 |
 v
Generate run ID
 |
 v
Create run directory
 |
 v
Collect run metadata
 |
 v
Create database adapter
 |
 v
Connect
 |
 v
Ingest canonical dataset
 |
 v
Validate node/relationship counts
 |
 v
Execute warmup queries
 |
 v
Execute measured queries
 |
 v
Calculate latency statistics
 |
 v
Collect ingestion statistics
 |
 v
Serialize database result
 |
 v
Clear benchmark data
 |
 v
Close database connection
```

The main orchestration is implemented by:

```text
benchmark/runner.py
```

---

## 9. Ingestion Flow

The ingestion layer is implemented in:

```text
benchmark/ingestion.py
```

The process is:

```text
nodes.csv
   |
   v
Database Adapter
   |
   v
Batch node insertion
   |
   v
relationships.csv
   |
   v
Batch relationship insertion
```

The ingestion benchmark records:

- total elapsed time
- nodes loaded
- relationships loaded
- nodes per second
- relationships per second

The configured batch size is part of the benchmark metadata.

---

## 10. Query Execution

Query execution is implemented in:

```text
benchmark/query.py
```

Each workload is executed using two phases.

### Warmup

Warmup executions are performed before measurement and are excluded from reported latency statistics.

### Measurement

The configured number of measured iterations is executed.

For each iteration the benchmark records query execution latency.

The benchmark calculates:

- minimum latency
- maximum latency
- mean latency
- P50
- P95
- P99
- QPS

---

## 11. Deterministic Query Parameters

Parameterized workloads use deterministic node IDs.

The query generator uses:

```text
query_seed = 42
```

The same seed produces the same sequence of node IDs.

This ensures that supported databases receive the same logical query parameter sequence instead of randomly selecting different nodes for every benchmark execution.

---

## 12. Result Limits

Traversal workloads can produce extremely large result sets for high-degree nodes.

To prevent a single query from exceeding a database's server-side row budget, the traversal workloads use:

```text
result_limit = 1000
```

for:

```text
traversal_1_hop
traversal_2_hop
traversal_3_hop
```

The limit is part of the workload definition and is applied consistently across the supported workload implementations.

---

## 13. Run Metadata

Every benchmark run receives a unique run ID.

The run ID uses the UTC timestamp format:

```text
YYYYMMDDTHHMMSSZ
```

Example:

```text
20260812T204838Z
```

Run metadata includes:

- run ID
- UTC timestamp
- Git commit
- Python version
- operating system/platform
- processor
- node count
- relationship count
- ingestion batch size
- query iterations
- query warmup iterations
- query seed

Metadata is written to:

```text
results/runs/<run_id>/metadata.json
```

---

## 14. Result Storage

Each benchmark run receives its own directory:

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

This structure prevents different benchmark runs from overwriting one another and allows individual runs to be traced back to their exact environment and Git revision.

---

## 15. Comparison Pipeline

Individual database results are combined into a comparison representation.

The comparison stage provides a common view of:

- ingestion performance
- query latency
- query throughput
- workload-level results
- database-level results

The comparison output is used as the input to the scoring stage.

---

## 16. Normalized Scoring

The scoring system is implemented in:

```text
benchmark/scoring.py
```

The benchmark uses best-value normalization.

For metrics where lower values are better:

```text
score = best_value / database_value
```

For metrics where higher values are better:

```text
score = database_value / best_value
```

Therefore:

```text
best performer = 1.0
```

Query latency uses:

```text
P95 latency
```

as the primary latency metric.

The overall score combines ingestion and query performance using the configured weighting methodology.

---

## 17. Analysis and Visualization

Additional benchmark modules provide:

- statistical analysis
- tail-latency analysis
- ranking
- normalized scoring
- result comparison
- visualization
- reporting

These stages operate on benchmark results rather than changing the underlying measurements.

This separation ensures that analysis does not alter the raw benchmark data.

---

## 18. Reproducibility

A benchmark result should be reproducible from:

1. the canonical dataset
2. database versions
3. deployment configuration
4. resource limits
5. benchmark configuration
6. workload definitions
7. query seed
8. Git commit
9. benchmark iteration counts
10. warmup configuration

The run metadata records the critical execution parameters required to trace a result back to the benchmark implementation.

---

## 19. Design Principles

### Database-specific logic stays isolated

Connection handling and database-specific query syntax belong in adapters and workload definitions.

### Benchmark orchestration remains database-agnostic

The runner operates through the common adapter and workload interfaces.

### Measurements are separated from analysis

Raw benchmark results are collected first. Comparison, scoring, statistics, and visualization operate afterward.

### Configuration is explicit

Dataset paths, expected counts, iteration counts, warmup counts, batch size, and query seed are explicit benchmark configuration values.

### Runs are traceable

Each run stores its own metadata and Git revision.

### Workloads are semantically equivalent

The query syntax may differ between databases, but each workload represents the same logical operation.

---

## 20. End-to-End Data Flow

The complete benchmark pipeline can be summarized as:

```text
Canonical Dataset
      |
      v
Database Adapter
      |
      v
Ingestion Benchmark
      |
      v
Dataset Validation
      |
      v
Deterministic Workload Execution
      |
      v
Latency + QPS Measurements
      |
      v
Raw Run Results
      |
      v
Statistical Analysis
      |
      v
Database Comparison
      |
      v
Normalized Scoring
      |
      v
Visualization / Reporting
```

The architecture is intentionally modular so that additional databases, workloads, statistical methods, or reporting outputs can be added without redesigning the core benchmark execution model.
