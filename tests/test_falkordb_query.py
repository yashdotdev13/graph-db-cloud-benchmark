from dotenv import load_dotenv

from benchmark.query import run_query_benchmark
from benchmark.workloads import ALL_WORKLOADS
from config.settings import load_database_config
from databases.falkordb import FalkorDBAdapter


load_dotenv()


def main() -> None:
    config = load_database_config("FALKORDB")

    adapter = FalkorDBAdapter(config)
    adapter.connect()

    try:
        print("Database:", adapter.name)
        print()

        for workload in ALL_WORKLOADS:
            print(f"Running workload: {workload.name}")

            result = run_query_benchmark(
                adapter,
                workload,
                iterations=20,
                warmup_iterations=5,
            )

            print(f"  Iterations: {result.iterations}")
            print(f"  Min:        {result.min_seconds * 1000:.3f} ms")
            print(f"  Mean:       {result.mean_seconds * 1000:.3f} ms")
            print(f"  P50:        {result.p50_seconds * 1000:.3f} ms")
            print(f"  P95:        {result.p95_seconds * 1000:.3f} ms")
            print(f"  P99:        {result.p99_seconds * 1000:.3f} ms")
            print(f"  Max:        {result.max_seconds * 1000:.3f} ms")
            print(f"  QPS:        {result.queries_per_second:.2f}")
            print()

        print("FalkorDB query benchmark: PASS")

    finally:
        adapter.close()


if __name__ == "__main__":
    main()