import json
from pathlib import Path
from typing import Any


LATENCY_METRICS = (
    "mean_ms",
    "min_ms",
    "p50_ms",
    "p95_ms",
    "p99_ms",
    "max_ms",
)

HIGHER_IS_BETTER = {
    "qps": True,
}

LOWER_IS_BETTER = {
    "mean_ms": True,
    "min_ms": True,
    "p50_ms": True,
    "p95_ms": True,
    "p99_ms": True,
    "max_ms": True,
}


def rank_values(
    values: dict[str, float],
    higher_is_better: bool,
) -> list[dict[str, Any]]:
    ranked = sorted(
        values.items(),
        key=lambda item: item[1],
        reverse=higher_is_better,
    )

    return [
        {
            "rank": rank,
            "database": database,
            "value": value,
        }
        for rank, (database, value) in enumerate(
            ranked,
            start=1,
        )
    ]


def build_rankings(
    comparison: dict[str, Any],
) -> dict[str, Any]:
    databases = comparison["databases"]

    rankings: dict[str, Any] = {
        "databases": databases,
        "ingestion": {},
        "queries": {},
    }

    # ---------------------------------------------------------
    # Ingestion rankings
    # ---------------------------------------------------------

    ingestion_metrics = (
        "elapsed_seconds",
        "nodes_per_second",
        "relationships_per_second",
    )

    for metric in ingestion_metrics:
        values = {
            database: comparison["ingestion"][database][metric]
            for database in databases
        }

        # elapsed_seconds -> lower is better
        # throughput -> higher is better
        higher_is_better = metric != "elapsed_seconds"

        rankings["ingestion"][metric] = rank_values(
            values,
            higher_is_better,
        )

    # ---------------------------------------------------------
    # Query rankings
    # ---------------------------------------------------------

    for workload, workload_results in comparison[
        "queries"
    ].items():

        rankings["queries"][workload] = {}

        for metric in (
            *LATENCY_METRICS,
            "qps",
        ):
            values = {
                database: workload_results[database][metric]
                for database in databases
            }

            higher_is_better = HIGHER_IS_BETTER.get(
                metric,
                False,
            )

            rankings["queries"][workload][metric] = (
                rank_values(
                    values,
                    higher_is_better,
                )
            )

    return rankings


def print_rankings(
    rankings: dict[str, Any],
) -> None:
    print()
    print("=" * 100)
    print("GRAPH DATABASE BENCHMARK RANKINGS")
    print("=" * 100)

    print()
    print("INGESTION")
    print("-" * 100)

    for metric, ranking in rankings["ingestion"].items():
        print()
        print(metric)

        for item in ranking:
            print(
                f"  {item['rank']}. "
                f"{item['database']:<12} "
                f"{item['value']:.3f}"
            )

    for workload, workload_rankings in rankings[
        "queries"
    ].items():

        print()
        print(workload.upper())
        print("-" * 100)

        for metric, ranking in workload_rankings.items():
            print()
            print(metric)

            for item in ranking:
                print(
                    f"  {item['rank']}. "
                    f"{item['database']:<12} "
                    f"{item['value']:.3f}"
                )


def save_rankings(
    rankings: dict[str, Any],
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
            rankings,
            file,
            indent=2,
        )


def main() -> None:
    comparison_path = Path(
        "results/comparison.json"
    )

    if not comparison_path.exists():
        raise FileNotFoundError(
            f"Comparison file not found: {comparison_path}"
        )

    with comparison_path.open(
        "r",
        encoding="utf-8",
    ) as file:
        comparison = json.load(file)

    rankings = build_rankings(comparison)

    print_rankings(rankings)

    output_path = Path(
        "results/rankings.json"
    )

    save_rankings(
        rankings,
        output_path,
    )

    print()
    print(f"Saved: {output_path}")


if __name__ == "__main__":
    main()
