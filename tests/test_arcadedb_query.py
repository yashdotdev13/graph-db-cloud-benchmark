from pathlib import Path

from dotenv import load_dotenv

from config.settings import load_database_config
from databases.arcadedb import ArcadeDBAdapter
from benchmark.query import run_query_benchmark
from benchmark.arcadedb_workloads import ALL_WORKLOADS


NODES_PATH = Path("data/processed/nodes.csv")
RELATIONSHIPS_PATH = Path("data/processed/relationships.csv")

EXPECTED_NODES = 36_692
EXPECTED_RELATIONSHIPS = 183_831


def print_result(result) -> None:
    print(f"\nRunning workload: {result.workload}")
    print(f"Iterations: {result.iterations}")
    print(f"Min:        {result.min_seconds * 1000:.3f} ms")
    print(f"Mean:       {result.mean_seconds * 1000:.3f} ms")
    print(f"P50:        {result.p50_seconds * 1000:.3f} ms")
    print(f"P95:        {result.p95_seconds * 1000:.3f} ms")
    print(f"P99:        {result.p99_seconds * 1000:.3f} ms")
    print(f"Max:        {result.max_seconds * 1000:.3f} ms")
    print(f"QPS:        {result.queries_per_second:.2f}")


def main() -> None:
    load_dotenv()

    config = load_database_config("ARCADEDB")
    adapter = ArcadeDBAdapter(config)

    adapter.connect()

    try:
        print("1. Clearing database...")
        adapter.clear()

        print("2. Loading nodes...")
        loaded_nodes = adapter.load_nodes(
            NODES_PATH,
            batch_size=1000,
        )
        print(f"   Nodes loaded: {loaded_nodes}")

        print("3. Loading relationships...")
        loaded_relationships = adapter.load_relationships(
            RELATIONSHIPS_PATH,
            batch_size=1000,
        )
        print(
            f"   Relationships loaded: "
            f"{loaded_relationships}"
        )

        print("4. Verifying counts...")

        node_count = adapter.count_nodes()
        relationship_count = adapter.count_relationships()

        print(f"   Node count: {node_count}")
        print(
            f"   Relationship count: "
            f"{relationship_count}"
        )

        assert node_count == EXPECTED_NODES
        assert relationship_count == EXPECTED_RELATIONSHIPS

        print("5. Running query benchmarks...")
        print(f"Database: {adapter.name}")

        for workload in ALL_WORKLOADS:
            result = run_query_benchmark(
                adapter,
                workload,
                iterations=20,
                warmup_iterations=5,
            )

            print_result(result)

        print("\nArcadeDB query benchmark: PASS")

    finally:
        print("\n6. Cleaning up...")
        adapter.clear()
        adapter.close()


if __name__ == "__main__":
    main()
