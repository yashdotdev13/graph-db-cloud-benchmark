import json
from dataclasses import asdict
from pathlib import Path

from benchmark.query import QueryBenchmarkResult
from benchmark.statistics import calculate_query_statistics


DATABASES = (
    "neo4j",
    "memgraph",
    "falkordb",
    "arcadedb",
    "cognodb",
)


def load_query_results(
    database: str,
) -> tuple[QueryBenchmarkResult, ...]:
    path = Path("results") / f"{database}.json"

    data = json.loads(
        path.read_text(encoding="utf-8")
    )

    return tuple(
        QueryBenchmarkResult(
            database=query["database"],
            workload=query["workload"],
            iterations=query["iterations"],
            warmup_iterations=query["warmup_iterations"],
            total_seconds=query["total_seconds"],
            latencies_seconds=tuple(
                query["latencies_seconds"]
            ),
        )
        for query in data["queries"]
    )


def main() -> None:
    statistics = []

    for database in DATABASES:
        results = load_query_results(database)

        for result in results:
            statistics.append(
                calculate_query_statistics(result)
            )

    print()
    print("=" * 100)
    print("GRAPH DATABASE STATISTICAL ANALYSIS")
    print("=" * 100)

    for stats in statistics:
        print()
        print(
            f"{stats.database.upper()} / "
            f"{stats.workload}"
        )
        print("-" * 60)
        print(
            f"Mean:        "
            f"{stats.mean_seconds * 1000:.3f} ms"
        )
        print(
            f"P50:         "
            f"{stats.p50_seconds * 1000:.3f} ms"
        )
        print(
            f"P95:         "
            f"{stats.p95_seconds * 1000:.3f} ms"
        )
        print(
            f"P99:         "
            f"{stats.p99_seconds * 1000:.3f} ms"
        )
        print(
            f"Stddev:      "
            f"{stats.standard_deviation_seconds * 1000:.3f} ms"
        )
        print(
            f"CV:          "
            f"{stats.coefficient_of_variation:.4f}"
        )
        print(
            f"P99/P50:     "
            f"{stats.p99_p50_ratio:.4f}"
        )

    output = Path("results/statistics.json")

    output.write_text(
        json.dumps(
            [
                asdict(stats)
                for stats in statistics
            ],
            indent=2,
        ),
        encoding="utf-8",
    )

    print()
    print(f"Saved: {output}")


if __name__ == "__main__":
    main()
