# Setup and Execution Guide

## 1. Overview

This document explains how to set up, verify, execute, and reproduce the
Graph Database Cloud Benchmark.

The benchmark evaluates:

- CognoDB
- Neo4j
- Memgraph
- FalkorDB
- ArcadeDB

The repository contains the Python benchmark framework and database
adapters. The self-hosted database instances are run separately using
Docker containers.

> **Important:** This repository does not contain Dockerfiles or a
> `docker-compose.yml`. Docker is used as the runtime environment for the
> self-hosted database instances.

CognoDB is accessed as a cloud database and is therefore configured through
its cloud connection details.

---

# 2. Architecture

The benchmark consists of three main parts:

```text
                         Graph Database Benchmark
                                  |
                    +-------------+-------------+
                    |                           |
             Python Benchmark              Database Layer
                    |                           |
          +---------+---------+       +---------+----------+
          |         |         |       |         |          |
       Dataset  Workloads  Runner   Neo4j  Memgraph  FalkorDB
          |         |         |       |         |          |
          |         |         |       +---------+----------+
          |         |         |                 |
          |         |         |              ArcadeDB
          |         |
          |         +-----------------------> CognoDB Cloud
          |
       CSV Dataset
```

The benchmark framework is responsible for:

- dataset loading
- database adapters
- workload execution
- warmup
- latency measurement
- QPS calculation
- result serialization
- comparison
- scoring
- visualization

Docker is responsible only for providing the self-hosted database
environments.

---

# 3. Prerequisites

Install the following software before running the benchmark.

## 3.1 Git

Verify:

```powershell
git --version
```

## 3.2 Python

The benchmark was developed and tested with Python 3.13.

Verify:

```powershell
python --version
```

Python 3.13 or a compatible supported Python version is recommended.

## 3.3 Docker Desktop

Docker Desktop is required for the self-hosted database instances:

- Neo4j
- Memgraph
- FalkorDB
- ArcadeDB

Verify:

```powershell
docker --version
```

Also verify that Docker is running:

```powershell
docker ps
```

---

# 4. Clone the Repository

```powershell
git clone https://github.com/yashdotdev13/graph-db-cloud-benchmark.git
cd graph-db-cloud-benchmark
```

---

# 5. Create the Python Virtual Environment

On Windows PowerShell:

```powershell
python -m venv .venv
```

Activate it:

```powershell
.venv\Scripts\Activate.ps1
```

After activation, the shell should show:

```text
(.venv)
```

If PowerShell prevents activation:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Then:

```powershell
.venv\Scripts\Activate.ps1
```

---

# 6. Install Python Dependencies

Upgrade pip:

```powershell
python -m pip install --upgrade pip
```

Install project dependencies:

```powershell
pip install -r requirements.txt
```

The benchmark uses dependencies for:

- Neo4j-compatible Bolt connectivity
- Redis/FalkorDB connectivity
- ArcadeDB HTTP connectivity
- environment-variable loading
- FalkorDB bulk ingestion
- Matplotlib visualization

The primary project dependencies are:

```text
neo4j
redis
requests
python-dotenv
falkordb-bulk-loader
matplotlib
```

---

# 7. Database Environment

## 7.1 Self-hosted databases

The following databases run in Docker containers:

```text
Neo4j
Memgraph
FalkorDB
ArcadeDB
```

The Docker containers are created separately from this repository.

The repository does not provide Dockerfiles or Docker Compose definitions
for these databases.

## 7.2 CognoDB

CognoDB is accessed through its cloud deployment.

Its connection details are configured through environment variables.

---

# 8. Database Versions

The benchmark methodology documents the versions used for the reported
benchmark.

| Database | Version | Deployment |
|---|---|---|
| CognoDB | 0.9.11 | Cloud |
| Neo4j | 5.26.29 | Docker |
| Memgraph | 3.12.0 | Docker |
| FalkorDB | 4.20.1 | Docker |
| ArcadeDB | 26.7.3 | Docker |

These versions are part of the benchmark environment.

See `docs/benchmark-methodology.md` for the complete methodology and
resource configuration.

---

# 9. Docker Database Setup

The benchmark uses Docker containers for the four self-hosted databases.

Start the required database containers before running the Python benchmark.

Verify running containers:

```powershell
docker ps
```

Verify all containers:

```powershell
docker ps -a
```

> The exact Docker deployment commands are intentionally not reproduced
> here because this repository does not contain Docker deployment files and
> the original PowerShell history does not preserve the complete multiline
> `docker run` commands. Use the documented database versions, ports, and
> resource envelope when provisioning the containers.

---

## 9.1 Neo4j

Neo4j is accessed through the Bolt protocol.

Configure:

```text
NEO4J_URI
NEO4J_USERNAME
NEO4J_PASSWORD
```

The benchmark environment used Neo4j 5.26.29.

Verify:

```powershell
docker ps
```

Inspect logs:

```powershell
docker logs <neo4j-container>
```

### Neo4j resource configuration

Neo4j requires explicit JVM memory configuration to operate within the
benchmark resource envelope.

The documented configuration is:

```text
Container memory:       512 MB
Container CPU:          0.5 vCPU
JVM heap maximum:       256 MB
Page cache:             128 MB
```

---

## 9.2 Memgraph

Memgraph is run as a Docker container and accessed through Bolt.

Configure:

```text
MEMGRAPH_URI
```

The benchmark environment used:

```text
bolt://localhost:7689
```

Verify:

```powershell
docker ps
```

You can check the database using `mgconsole`:

```powershell
docker exec -i <memgraph-container> mgconsole `
    --host 127.0.0.1 `
    --port 7687
```

---

## 9.3 FalkorDB

FalkorDB is run in Docker and accessed through Redis.

Configure:

```text
FALKORDB_HOST
FALKORDB_PORT
```

The benchmark environment used:

```text
FALKORDB_HOST=localhost
FALKORDB_PORT=6380
```

Verify Redis connectivity:

```powershell
docker exec <falkordb-container> redis-cli PING
```

Expected:

```text
PONG
```

Test graph query execution:

```powershell
docker exec <falkordb-container> redis-cli `
    GRAPH.QUERY testgraph "RETURN 1"
```

The benchmark also uses the FalkorDB bulk ingestion tool:

```text
falkordb-bulk-insert
```

Verify it is available:

```powershell
Get-Command falkordb-bulk-insert
```

---

## 9.4 ArcadeDB

ArcadeDB is run as a Docker container and accessed through its HTTP
interface.

Configure:

```text
ARCADEDB_HOST
ARCADEDB_PORT
ARCADEDB_USERNAME
ARCADEDB_PASSWORD
ARCADEDB_DATABASE
```

The benchmark environment used:

```text
ARCADEDB_HOST=localhost
ARCADEDB_PORT=2481
ARCADEDB_USERNAME=root
ARCADEDB_DATABASE=testgraph
```

Verify:

```powershell
docker ps
```

Inspect logs:

```powershell
docker logs <arcadedb-container>
```

ArcadeDB can also be checked using its console inside the container.

---

# 10. Environment Configuration

Create the local environment file from the template:

```powershell
Copy-Item .env.example .env
```

Open it:

```powershell
notepad .env
```

Configure the required values:

```text
# CognoDB
COGNODB_URI=
COGNODB_USERNAME=
COGNODB_PASSWORD=

# Neo4j
NEO4J_URI=bolt://localhost:7688
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=

# Memgraph
MEMGRAPH_URI=bolt://localhost:7689

# FalkorDB
FALKORDB_HOST=localhost
FALKORDB_PORT=6380

# ArcadeDB
ARCADEDB_HOST=localhost
ARCADEDB_PORT=2481
ARCADEDB_USERNAME=root
ARCADEDB_PASSWORD=
ARCADEDB_DATABASE=testgraph
```

Do not commit `.env`.

The repository excludes `.env` through `.gitignore`.

---

# 11. Dataset

The benchmark uses the canonical processed dataset:

```text
data/processed/nodes.csv
data/processed/relationships.csv
```

The current benchmark dataset contains:

```text
36,692 nodes
183,831 relationships
```

The benchmark discovers dataset counts dynamically before execution.

The runner then verifies that the database contains the expected number of
nodes and relationships after ingestion.

---

# 12. Verify the Dataset

Check both files:

```powershell
Test-Path data/processed/nodes.csv
Test-Path data/processed/relationships.csv
```

Expected:

```text
True
True
```

---

# 13. Verify the Python Installation

Compile the project modules:

```powershell
python -m compileall benchmark databases config
```

A successful run should finish without compilation errors.

---

# 14. Verify Database Adapter Registration

Run:

```powershell
python -c "from benchmark.database_registry import create_adapter; print([create_adapter(name).name for name in ['NEO4J','MEMGRAPH','FALKORDB','ARCADEDB','COGNODB']])"
```

Expected:

```text
['neo4j', 'memgraph', 'falkordb', 'arcadedb', 'cognodb']
```

This confirms that all five database adapters are registered.

---

# 15. Verify Workload Registration

Run:

```powershell
python -c "from benchmark.workload_registry import get_workloads; [print(name, [w.name for w in get_workloads(name)]) for name in ['NEO4J','MEMGRAPH','FALKORDB','ARCADEDB','COGNODB']]"
```

Each database should expose:

```text
point_lookup
indexed_lookup
relationship_lookup
traversal_1_hop
traversal_2_hop
traversal_3_hop
aggregation
```

The workload implementations use database-specific query syntax where
required while preserving the same logical benchmark operation.

---

# 16. Run a Small Validation Benchmark

Before a complete benchmark, perform a short validation run:

```powershell
python -m benchmark.cli --database NEO4J --iterations 10 --warmup 2
```

A successful run prints the benchmark run information, ingestion results,
and query workload results.

The result is saved under:

```text
results/runs/<run_id>/
```

---

# 17. Run a Single Database

Select one database with:

```powershell
python -m benchmark.cli --database NEO4J
```

Supported values:

```text
NEO4J
MEMGRAPH
FALKORDB
ARCADEDB
COGNODB
```

Example:

```powershell
python -m benchmark.cli --database COGNODB
```

---

# 18. Run the Complete Benchmark

Run all supported databases:

```powershell
python -m benchmark.cli --all
```

Default configuration:

```text
Measured iterations:  100
Warmup iterations:    10
Query seed:           42
Ingestion batch size: 1000
```

---

# 19. Custom Benchmark Iterations

Short validation:

```powershell
python -m benchmark.cli --all --iterations 10 --warmup 2
```

Standard benchmark:

```powershell
python -m benchmark.cli --all --iterations 100 --warmup 10
```

Warmup executions are excluded from measured latency statistics.

---

# 20. Benchmark Execution Flow

For every selected database:

```text
Connect
   |
   v
Clear previous benchmark data
   |
   v
Load nodes
   |
   v
Load relationships
   |
   v
Validate node count
   |
   v
Validate relationship count
   |
   v
Warmup queries
   |
   v
Measured queries
   |
   v
Calculate statistics
   |
   v
Serialize results
   |
   v
Clear benchmark data
   |
   v
Close connection
```

The `GraphDatabaseAdapter` interface provides the common operations required
by each database adapter.

---

# 21. Query Measurement

The query benchmark uses:

- deterministic query parameters
- deterministic random seed
- warmup iterations
- measured iterations
- individual latency measurements

The query seed is:

```text
42
```

For workloads using node IDs, IDs are generated deterministically from this
seed.

The benchmark records:

```text
Minimum
Maximum
Mean
P50
P95
P99
QPS
```

P95 is used as the primary latency metric for normalized scoring because it
captures tail behavior better than mean latency.

---

# 22. Traversal Result Bounds

Traversal workloads use an explicit result limit.

The following workloads are bounded to 1,000 returned rows:

```text
traversal_1_hop
traversal_2_hop
traversal_3_hop
```

This prevents very large traversal result sets from exceeding server-side
row budgets.

The bound is part of the benchmark workload definition and is applied
consistently across the supported database workloads.

---

# 23. Benchmark Results

Every benchmark execution receives a unique run ID.

Example:

```text
results/runs/20260812T213345Z/
```

A run directory can contain:

```text
metadata.json
<database>.json
```

Metadata records information such as:

- run ID
- UTC timestamp
- Git commit
- Python version
- operating system
- processor
- node count
- relationship count
- ingestion batch size
- query iterations
- warmup iterations
- query seed

---

# 24. Comparison

After benchmark runs have been collected, the comparison stage can be
executed using the repository's comparison module:

```powershell
python -m benchmark.comparison
```

The comparison consolidates database results for analysis.

Generated comparison artifacts are stored under:

```text
results/
```

---

# 25. Normalized Scoring

Generate normalized scores:

```powershell
python -m benchmark.scoring
```

The scoring methodology uses:

```text
Primary query latency metric: P95
Normalization: best-value normalization
```

The generated score file is:

```text
results/scores.json
```

The detailed scoring methodology is documented in:

```text
docs/results_and_scoring.md
```

The overall score uses:

```text
20% ingestion performance
80% query performance
```

Within query performance, workloads are averaged and each workload combines:

```text
50% P95 latency score
50% QPS score
```

---

# 26. Visualization

The project includes Matplotlib-based visualization.

Run the visualization module provided by the repository:

```powershell
python -m benchmark.visualization
```

Generated charts are stored under the configured results/chart output
directory.

Visualizations are intended to make latency, throughput, QPS, and normalized
scores easier to compare.

---

# 27. Reproducibility

To reproduce the reported benchmark as closely as possible, use:

- the same database versions
- the same Docker resource envelope
- the same dataset
- the same workload definitions
- the same query seed
- the same iteration count
- the same warmup count
- the same ingestion batch size
- the same Python environment
- the same Git revision

Each benchmark run records the Git commit in its metadata.

The complete methodology is documented in:

```text
docs/benchmark-methodology.md
```

---

# 28. Resource Envelope

The reported benchmark uses:

| Resource | Target |
|---|---:|
| CPU | 0.5 vCPU |
| Memory | 512 MB |
| Storage | 1 GB target |

Neo4j additionally uses:

```text
JVM heap maximum: 256 MB
Page cache:       128 MB
```

The CognoDB free-tier environment available for the benchmark provided
512 MB RAM and burstable 0.5 vCPU with 1 GiB storage.

The assignment described 256 MB RAM, but a 256 MB CognoDB configuration was
not available. Therefore, the available CognoDB c0 configuration was used
and the self-hosted databases were constrained to the same target envelope.

See `docs/benchmark-methodology.md` for the complete discussion.

---

# 29. Troubleshooting

## 29.1 Docker is not running

Check:

```powershell
docker ps
```

If Docker is unavailable, start Docker Desktop and retry.

---

## 29.2 Database container is not running

Check:

```powershell
docker ps -a
```

Inspect logs:

```powershell
docker logs <container-name>
```

---

## 29.3 Python dependency error

Recreate the virtual environment:

```powershell
deactivate
Remove-Item -Recurse -Force .venv
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

## 29.4 Database connection failure

Check:

1. Docker container status
2. exposed ports
3. `.env` configuration
4. database credentials
5. database health
6. database version

---

## 29.5 CognoDB connection failure

Verify:

```text
COGNODB_URI
COGNODB_USERNAME
COGNODB_PASSWORD
```

CognoDB is cloud-hosted and requires valid credentials.

---

## 29.6 FalkorDB connectivity failure

Run:

```powershell
docker exec <falkordb-container> redis-cli PING
```

Expected:

```text
PONG
```

Also verify the bulk loader:

```powershell
Get-Command falkordb-bulk-insert
```

---

## 29.7 Dataset not found

Run:

```powershell
Test-Path data/processed/nodes.csv
Test-Path data/processed/relationships.csv
```

Both should return:

```text
True
```

---

## 29.8 Query result-limit errors

Traversal workloads intentionally include a result bound to prevent
extremely large result sets from exceeding database/server row budgets.

The benchmark therefore measures bounded traversal workloads rather than
unbounded result materialization.

---

# 30. Security

Never commit:

```text
.env
```

The `.env.example` file contains placeholders only.

Do not place the following in tracked files:

- database passwords
- cloud credentials
- API keys
- access tokens

The `.gitignore` excludes `.env`.

---

# 31. Recommended Fresh-Machine Execution Sequence

Use the following order:

```text
1. Install Git
       |
2. Install Python
       |
3. Install Docker Desktop
       |
4. Clone repository
       |
5. Create Python virtual environment
       |
6. Install requirements.txt
       |
7. Provision/start self-hosted database containers
       |
8. Configure .env
       |
9. Start/verify databases
       |
10. Verify dataset
       |
11. Verify database registry
       |
12. Verify workload registry
       |
13. Run small validation benchmark
       |
14. Run full benchmark
       |
15. Generate comparison
       |
16. Generate normalized scores
       |
17. Generate visualizations
       |
18. Review results
```

---

# 32. Related Documentation

Additional project documentation:

```text
docs/benchmark-methodology.md
docs/results_and_scoring.md
docs/setup-and-execution.md
```

The root `README.md` provides the high-level project overview.

---

# 33. Important Reproduction Note

This repository contains the benchmark implementation, database adapters,
workload definitions, scoring logic, and configuration templates.

It does not contain Dockerfiles or Docker Compose deployment definitions.

The self-hosted database environments therefore need to be provisioned
separately.

The reported benchmark results depend on the documented:

- database versions
- deployment model
- resource envelope
- dataset
- workload suite
- query configuration
- benchmark iteration configuration
- software revision

The results should therefore be interpreted as measurements of the
documented benchmark environment and not as universal rankings of graph
database systems.
