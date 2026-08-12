# Benchmark Methodology

## Resource Envelope

All databases are benchmarked using the same target resource
envelope wherever the deployment model permits:

- CPU: 0.5 vCPU
- Memory: 512 MB
- Storage: 1 GB target

The CognoDB Cloud free tier currently provides 512 MB RAM,
burstable to 0.5 vCPU, with 1 GiB storage.

The assignment describes the CognoDB free tier as 256 MB RAM.
However, the currently available CognoDB c0 configuration
provides 512 MB RAM and no 256 MB configuration was available.

Therefore, the benchmark uses the currently available c0
configuration and constrains all self-hosted databases to the
same 512 MB / 0.5 CPU envelope.

## Database Versions

| Database | Version | Deployment |
|---|---|---|
| CognoDB | 0.9.11 | Cloud |
| Neo4j | 5.26.29 | Docker |
| Memgraph | 3.12.0 | Docker |
| FalkorDB | 4.20.1 | Docker |
| ArcadeDB | 26.7.3 | Docker |

## Preflight Verification

Before benchmark implementation, each database was verified
under the target resource envelope.

The preflight included:

1. Database startup verification
2. Connectivity verification
3. Simple query execution
4. Vertex/node creation
5. Basic lookup/count verification

All five databases successfully passed the preflight.

## Neo4j Memory Configuration

Neo4j required explicit JVM memory configuration to operate
within the 512 MB container limit.

The preflight configuration used:

- Container memory: 512 MB
- Container CPU: 0.5 vCPU
- JVM heap maximum: 256 MB
- Page cache: 128 MB

Neo4j successfully started and passed functional queries
without being OOM-killed.

## Benchmark Fairness

The benchmark compares database performance under a common
resource envelope rather than unrestricted default configurations.

Database-specific memory management settings required for
successful operation within the envelope will be documented
and retained as part of the benchmark configuration.

Results will be interpreted within the context of these
controlled resource constraints.