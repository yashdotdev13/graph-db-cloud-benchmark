import csv
import json
from pathlib import Path
from typing import Any


DATABASES = (
    "neo4j",
    "memgraph",
    "falkordb",
    "arcadedb",
    "cognodb",
)


def load_results(results_dir: Path) -> dict[str, dict[str, Any]]:
    results: dict[str, dict[str, Any]] = {}

    for database in DATABASES:
        path = results_dir / f"{database}.json"

        if not path.exists():
            raise FileNotFoundError(
                f"Result file not found: {path}"
            )

        with path.open(
            "r",
            encoding="utf-8",
        ) as file:
            results[database] = json.load(file)

    return results


def build_comparison(
    results: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    comparison: dict[str, Any] = {
        "databases": list(results.keys()),
        "ingestion": {},
        "queries": {},
    }

    for database, summary in results.items():
        ingestion = summary["ingestion"]

        comparison["ingestion"][database] = {
            "node_count": ingestion["node_count"],
            "relationship_count": ingestion["relationship_count"],
            "elapsed_seconds": ingestion["elapsed_seconds"],
            "nodes_per_second": (
                ingestion["node_count"]
                / ingestion["elapsed_seconds"]
            ),
            "relationships_per_second": (
                ingestion["relationship_count"]
                / ingestion["elapsed_seconds"]
            ),
        }

        for query in summary["queries"]:
            workload = query["workload"]

            if workload not in comparison["queries"]:
                comparison["queries"][workload] = {}

            latencies = query["latencies_seconds"]

            sorted_latencies = sorted(latencies)

            comparison["queries"][workload][database] = {
                "iterations": query["iterations"],
                "warmup_iterations": query[
                    "warmup_iterations"
                ],
                "mean_ms": (
                    sum(latencies)
                    / len(latencies)
                    * 1000
                ),
                "min_ms": min(latencies) * 1000,
                "p50_ms": percentile(
                    sorted_latencies,
                    50,
                ) * 1000,
                "p95_ms": percentile(
                    sorted_latencies,
                    95,
                ) * 1000,
                "p99_ms": percentile(
                    sorted_latencies,
                    99,
                ) * 1000,
                "max_ms": max(latencies) * 1000,
                "qps": (
                    query["iterations"]
                    / query["total_seconds"]
                ),
            }

    return comparison


def percentile(
    values: list[float],
    percentile_value: float,
) -> float:
    if not values:
        raise ValueError(
            "Cannot calculate percentile of empty data"
        )

    if len(values) == 1:
        return values[0]

    position = (
        percentile_value / 100
    ) * (len(values) - 1)

    lower = int(position)
    upper = lower + 1

    if upper >= len(values):
        return values[lower]

    weight = position - lower

    return (
        values[lower]
        + (values[upper] - values[lower]) * weight
    )


def print_comparison(
    comparison: dict[str, Any],
) -> None:
    databases = comparison["databases"]

    print()
    print("=" * 100)
    print("GRAPH DATABASE BENCHMARK COMPARISON")
    print("=" * 100)

    print()
    print("INGESTION")
    print("-" * 100)

    print(
        f"{'Database':<12}"
        f"{'Time(s)':>12}"
        f"{'Nodes/sec':>15}"
        f"{'Relationships/sec':>22}"
    )

    for database in databases:
        result = comparison["ingestion"][database]

        print(
            f"{database:<12}"
            f"{result['elapsed_seconds']:>12.3f}"
            f"{result['nodes_per_second']:>15.2f}"
            f"{result['relationships_per_second']:>22.2f}"
        )

    for workload, database_results in comparison[
        "queries"
    ].items():
        print()
        print(workload.upper())
        print("-" * 100)

        print(
            f"{'Database':<12}"
            f"{'Mean(ms)':>12}"
            f"{'P50(ms)':>12}"
            f"{'P95(ms)':>12}"
            f"{'P99(ms)':>12}"
            f"{'QPS':>12}"
        )

        for database in databases:
            result = database_results[database]

            print(
                f"{database:<12}"
                f"{result['mean_ms']:>12.3f}"
                f"{result['p50_ms']:>12.3f}"
                f"{result['p95_ms']:>12.3f}"
                f"{result['p99_ms']:>12.3f}"
                f"{result['qps']:>12.2f}"
            )


def save_comparison_json(
    comparison: dict[str, Any],
    output_path: Path,
) -> None:
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with output_path.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            comparison,
            file,
            indent=2,
        )


def save_comparison_csv(
    comparison: dict[str, Any],
    output_path: Path,
) -> None:
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    rows: list[dict[str, Any]] = []

    for database in comparison["databases"]:
        ingestion = comparison["ingestion"][database]

        rows.append(
            {
                "database": database,
                "category": "ingestion",
                "workload": "",
                "metric": "elapsed_seconds",
                "value": ingestion[
                    "elapsed_seconds"
                ],
            }
        )

        rows.append(
            {
                "database": database,
                "category": "ingestion",
                "workload": "",
                "metric": "nodes_per_second",
                "value": ingestion[
                    "nodes_per_second"
                ],
            }
        )

        rows.append(
            {
                "database": database,
                "category": "ingestion",
                "workload": "",
                "metric": "relationships_per_second",
                "value": ingestion[
                    "relationships_per_second"
                ],
            }
        )

    for workload, database_results in comparison[
        "queries"
    ].items():
        for database in comparison["databases"]:
            result = database_results[database]

            for metric in (
                "mean_ms",
                "min_ms",
                "p50_ms",
                "p95_ms",
                "p99_ms",
                "max_ms",
                "qps",
            ):
                rows.append(
                    {
                        "database": database,
                        "category": "query",
                        "workload": workload,
                        "metric": metric,
                        "value": result[metric],
                    }
                )

    with output_path.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "database",
                "category",
                "workload",
                "metric",
                "value",
            ],
        )

        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    results_dir = Path("results")

    results = load_results(results_dir)

    comparison = build_comparison(results)

    print_comparison(comparison)

    json_path = results_dir / "comparison.json"
    csv_path = results_dir / "comparison.csv"

    save_comparison_json(
        comparison,
        json_path,
    )

    save_comparison_csv(
        comparison,
        csv_path,
    )

    print()
    print(f"Saved: {json_path}")
    print(f"Saved: {csv_path}")


if __name__ == "__main__":
    main()
