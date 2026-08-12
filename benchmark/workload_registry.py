from benchmark.workload import BenchmarkWorkload
from benchmark.arcadedb_workloads import ALL_WORKLOADS as ARCADEDB_WORKLOADS
from benchmark.cognodb_workloads import ALL_WORKLOADS as COGNODB_WORKLOADS
from benchmark.memgraph_workloads import ALL_WORKLOADS as MEMGRAPH_WORKLOADS
from benchmark.neo4j_workloads import ALL_WORKLOADS as NEO4J_WORKLOADS
from benchmark.workloads import ALL_WORKLOADS as FALKORDB_WORKLOADS


WORKLOAD_REGISTRY: dict[str, tuple[BenchmarkWorkload, ...]] = {
    "NEO4J": NEO4J_WORKLOADS,
    "MEMGRAPH": MEMGRAPH_WORKLOADS,
    "FALKORDB": FALKORDB_WORKLOADS,
    "ARCADEDB": ARCADEDB_WORKLOADS,
    "COGNODB": COGNODB_WORKLOADS,
}


def get_workloads(database: str) -> tuple[BenchmarkWorkload, ...]:
    name = database.upper()

    try:
        return WORKLOAD_REGISTRY[name]
    except KeyError:
        raise ValueError(
            f"No workloads registered for database: {database}"
        )
