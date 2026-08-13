# Workload Reference

## 1. Purpose

This document defines the benchmark workload suite used to compare the supported graph databases.

The benchmark evaluates equivalent logical operations across:

- Neo4j
- Memgraph
- FalkorDB
- ArcadeDB
- CognoDB

The query syntax may differ between database systems, but the intended operation and benchmark semantics remain consistent.

Database-specific workload definitions are maintained separately so that query-language differences do not leak into the benchmark runner.

---

## 2. Workload Model

Workloads are represented by the `BenchmarkWorkload` dataclass:

```text
benchmark/workload.py
```

A workload contains:

- `name`
- `description`
- `query`
- optional `parameters`
- optional `result_limit`

The benchmark runner executes workloads through this common model.

The workload registry is:

```text
benchmark/workload_registry.py
```

It maps each supported database to its workload definitions.

---

## 3. Workload Suite

The current benchmark contains seven logical workloads:

| Workload | Purpose |
|---|---|
| `point_lookup` | Lookup one user by ID |
| `indexed_lookup` | Exercise indexed user lookup |
| `relationship_lookup` | Find direct `KNOWS` relationships |
| `traversal_1_hop` | Traverse exactly one hop |
| `traversal_2_hop` | Traverse exactly two hops |
| `traversal_3_hop` | Traverse exactly three hops |
| `aggregation` | Count all benchmark users |

Each workload is executed using the configured warmup and measurement iterations.

---

## 4. Point Lookup

### Workload name

```text
point_lookup
```

### Purpose

Measures the latency of locating a single `User` node using its `id` property.

### Logical operation

```text
Find User where id = <node_id>
```

### Parameters

```text
id
```

The benchmark supplies the ID parameter dynamically.

### Cypher-style implementation

```cypher
MATCH (u:User {id: $id})
RETURN u
```

### What it measures

This workload primarily measures point-access latency for a single graph node.

---

## 5. Indexed Lookup

### Workload name

```text
indexed_lookup
```

### Purpose

Measures lookup performance using the benchmark's indexed access path.

### Logical operation

```text
Find User where indexed id = <node_id>
```

The exact query syntax and index mechanism are database-specific.

### Why it is separate from point lookup

An indexed lookup explicitly evaluates the database's indexed access path rather than treating all node-property lookups as equivalent.

This allows the benchmark to distinguish ordinary point lookup behavior from indexed lookup behavior.

### Database-specific implementation

The query is defined independently for each supported database where the underlying database supports the required indexed lookup semantics.

The benchmark runner treats the workload as a logical operation and does not hard-code database-specific query syntax.

---

## 6. Relationship Lookup

### Workload name

```text
relationship_lookup
```

### Purpose

Measures the cost of finding direct outgoing `KNOWS` relationships from a user.

### Logical operation

```text
Find all users directly connected by KNOWS from <node_id>
```

### Parameters

```text
id
```

### Cypher-style implementation

```cypher
MATCH (u:User {id: $id})-[:KNOWS]->(friend)
RETURN friend
```

### What it measures

This workload measures direct graph relationship access and the cost of retrieving first-degree neighbors.

---

## 7. Traversal Workloads

Traversal is divided into three separate workloads instead of combining all depths into one query.

This makes latency behavior visible as traversal depth increases.

---

### 7.1 One-Hop Traversal

### Workload name

```text
traversal_1_hop
```

### Logical operation

```text
Traverse exactly one KNOWS relationship.
```

### Cypher-style implementation

```cypher
MATCH (u:User {id: $id})-[:KNOWS]->(friend)
RETURN friend
LIMIT 1000
```

---

### 7.2 Two-Hop Traversal

### Workload name

```text
traversal_2_hop
```

### Logical operation

```text
Traverse exactly two KNOWS relationships.
```

### Cypher-style implementation

```cypher
MATCH (u:User {id: $id})-[:KNOWS*2]->(friend)
RETURN friend
LIMIT 1000
```

---

### 7.3 Three-Hop Traversal

### Workload name

```text
traversal_3_hop
```

### Logical operation

```text
Traverse exactly three KNOWS relationships.
```

### Cypher-style implementation

```cypher
MATCH (u:User {id: $id})-[:KNOWS*3]->(friend)
RETURN friend
LIMIT 1000
```

---

## 8. Traversal Result Limit

All three traversal workloads use:

```text
result_limit = 1000
```

The limit exists because graph traversal can produce extremely large result sets for high-degree nodes.

During validation, an unrestricted traversal produced a server-side row-budget failure in CognoDB for a high-degree node.

The benchmark therefore bounds traversal results to 1000 rows.

The purpose of this limit is operational stability and workload comparability.

The limit is applied to the workload definitions rather than implemented as a database-specific exception in the runner.

---

## 9. Aggregation

### Workload name

```text
aggregation
```

### Purpose

Measures the cost of counting all benchmark users.

### Logical operation

```text
Count all User nodes.
```

### Cypher-style implementation

```cypher
MATCH (u:User)
RETURN count(u)
```

### What it measures

Unlike point and traversal workloads, aggregation operates over the complete node population.

It therefore provides a workload representing global graph scanning/aggregation behavior.

---

## 10. Parameters and Deterministic Query Selection

Parameterized workloads use the `id` parameter.

The benchmark generates node IDs deterministically using:

```text
query_seed = 42
```

The generator is implemented in:

```text
benchmark/query.py
```

The same seed produces the same node-ID sequence.

For example, the benchmark sequence generated from seed `42` begins with:

```text
7296
1639
18024
16049
14628
9144
6717
35741
5697
27651
```

The same sequence is used when comparing databases under the same benchmark configuration.

This prevents random query selection from becoming an uncontrolled source of variation.

---

## 11. Warmup and Measurement

Every query workload is divided into two phases.

### Warmup phase

Configured warmup iterations are executed first.

Warmup executions are excluded from latency statistics.

The purpose is to allow database and runtime state to settle before measurements are collected.

### Measurement phase

The configured measurement iterations are then executed.

Each measured execution records its elapsed query time.

The resulting measurements are used to calculate:

- minimum latency
- maximum latency
- mean latency
- P50
- P95
- P99
- QPS

---

## 12. Query Latency Measurement

Query execution timing is implemented in:

```text
benchmark/query.py
```

Each measured query execution uses a high-resolution performance timer.

The benchmark records the individual latency values and calculates the summary statistics afterward.

P95 is used by the scoring methodology as the primary latency metric because it captures tail behavior better than the arithmetic mean.

---

## 13. Query Throughput

Query throughput is reported as queries per second:

```text
QPS = iterations / total_measurement_time
```

QPS is treated as a higher-is-better metric during normalized scoring.

The total measurement interval includes the measured query executions and excludes the warmup phase.

---

## 14. Database-Specific Workload Definitions

The workload files are organized as follows:

```text
benchmark/
├── workloads.py
├── neo4j_workloads.py
├── memgraph_workloads.py
├── arcadedb_workloads.py
└── cognodb_workloads.py
```

FalkorDB currently uses the shared Cypher-style workload definitions in:

```text
benchmark/workloads.py
```

The registry connects each database to its workload tuple.

---

## 15. Query Language Differences

The benchmark does not require identical query strings across databases.

Instead, it requires equivalent logical semantics.

For example, the Cypher-style databases can express traversal as:

```cypher
MATCH (u:User {id: $id})-[:KNOWS*2]->(friend)
RETURN friend
LIMIT 1000
```

ArcadeDB uses its own query/traversal syntax to represent the same logical operation.

This separation is intentional.

Forcing identical query syntax across different graph database engines would not produce a meaningful comparison when the engines expose different query languages and execution models.

---

## 16. Workload Equivalence

Workload equivalence is defined at the logical-operation level.

For each database, the implementation should satisfy the same intended operation:

| Workload | Required semantic operation |
|---|---|
| `point_lookup` | Locate one user by ID |
| `indexed_lookup` | Locate one user through the indexed access path |
| `relationship_lookup` | Retrieve direct `KNOWS` neighbors |
| `traversal_1_hop` | Traverse exactly one `KNOWS` hop |
| `traversal_2_hop` | Traverse exactly two `KNOWS` hops |
| `traversal_3_hop` | Traverse exactly three `KNOWS` hops |
| `aggregation` | Count all benchmark users |

The benchmark runner does not contain database-specific query strings.

This keeps the benchmark orchestration independent from individual query languages.

---

## 17. Workload Ordering

The benchmark executes workloads in the order provided by the database's registered workload tuple.

The standard workload order is:

```text
point_lookup
indexed_lookup
relationship_lookup
traversal_1_hop
traversal_2_hop
traversal_3_hop
aggregation
```

Keeping a stable ordering makes console output and result files easier to compare.

---

## 18. Workload Validation

Before using a workload in a full benchmark run, its query implementation can be validated against the target database.

Validation should confirm:

1. the query parses successfully
2. the required parameters are accepted
3. the query executes successfully
4. the intended graph operation is performed
5. result limits are respected where applicable

Diagnostic workload validation scripts used during development are not part of the permanent benchmark suite.

---

## 19. Workload Configuration

Workload definitions should remain declarative wherever possible.

The benchmark runner should be responsible for:

- selecting workloads
- generating deterministic parameters
- performing warmup
- measuring latency
- calculating statistics

The workload definitions should be responsible for:

- describing the logical operation
- providing database-specific query syntax
- defining default parameters
- declaring result limits

This separation prevents benchmark execution logic from becoming coupled to individual query implementations.

---

## 20. Summary

The workload system provides a stable logical contract across the five supported graph databases.

The benchmark currently measures:

```text
Point lookup
      |
Indexed lookup
      |
Relationship lookup
      |
1-hop traversal
      |
2-hop traversal
      |
3-hop traversal
      |
Aggregation
```

Parameterized workloads use deterministic query selection with seed `42`.

Traversal workloads are bounded to 1000 returned rows.

Warmup executions are excluded from measurements.

Measured executions produce latency and throughput statistics.

Database-specific query syntax remains isolated inside workload definitions while the benchmark runner operates on a common workload abstraction.
