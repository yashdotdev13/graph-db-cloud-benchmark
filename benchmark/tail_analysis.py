import json
from dataclasses import asdict, dataclass
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


@dataclass(frozen=True)
class TailLatencyAnalysis:
    database: str
    workload: str
    p95_p50_ratio: float
    p99_p50_ratio: float
    max_p50_ratio: float
    coefficient_of_variation: float


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


def analyze_tail_latency(
    result: QueryBenchmarkResult,
) -> TailLatencyAnalysis:
    statistics = calculate_query_statistics(result)

    if statistics.p50_seconds <= 0:
        raise ValueError(
            "P50 latency must be greater than zero."
        )

    return TailLatencyAnalysis(
        database=statistics.database,
        workload=statistics.workload,
        p95_p50_ratio=(
            statistics.p95_seconds
            / statistics.p50_seconds
        ),
        p99_p50_ratio=(
            statistics.p99_seconds
            / statistics.p50_seconds
        ),
        max_p50_ratio=(
            statistics.max_seconds
            / statistics.p50_seconds
        ),
        coefficient_of_variation=(
            statistics.coefficient_of_variation
        ),
    )


def main() -> None:
    analyses = []

    for database in DATABASES:
        results = load_query_results(database)

        for result in results:
            analyses.append(
                analyze_tail_latency(result)
            )

    print()
    print("=" * 100)
    print("GRAPH DATABASE TAIL-LATENCY ANALYSIS")
    print("=" * 100)

    for analysis in analyses:
        print()
        print(
            f"{analysis.database.upper()} / "
            f"{analysis.workload}"
        )
        print("-" * 60)
        print(
            f"P95/P50:     "
            f"{analysis.p95_p50_ratio:.4f}x"
        )
        print(
            f"P99/P50:     "
            f"{analysis.p99_p50_ratio:.4f}x"
        )
        print(
            f"Max/P50:     "
            f"{analysis.max_p50_ratio:.4f}x"
        )
        print(
            f"CV:          "
            f"{analysis.coefficient_of_variation:.4f}"
        )

    output = Path(
        "results/tail_analysis.json"
    )

    output.write_text(
        json.dumps(
            [
                asdict(analysis)
                for analysis in analyses
            ],
            indent=2,
        ),
        encoding="utf-8",
    )

    print()
    print(f"Saved: {output}")


if __name__ == "__main__":
    main()
