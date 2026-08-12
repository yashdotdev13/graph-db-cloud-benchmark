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


# P95 is used as the primary latency metric because
# it represents tail behavior better than the mean.
QUERY_LATENCY_METRIC = "p95_ms"


def lower_is_better_score(
    values: dict[str, float],
) -> dict[str, float]:
    best = min(values.values())

    return {
        database: best / value
        for database, value in values.items()
    }


def higher_is_better_score(
    values: dict[str, float],
) -> dict[str, float]:
    best = max(values.values())

    return {
        database: value / best
        for database, value in values.items()
    }


def build_scores(
    comparison: dict[str, Any],
) -> dict[str, Any]:

    databases = comparison["databases"]

    scores: dict[str, Any] = {
        "databases": databases,
        "methodology": {
            "query_latency_metric": QUERY_LATENCY_METRIC,
            "normalization": "best_value_normalization",
        },
        "ingestion": {},
        "queries": {},
        "overall": {},
    }

    # ---------------------------------------------------------
    # Ingestion
    # ---------------------------------------------------------

    ingestion_time = {
        database: comparison["ingestion"][database][
            "elapsed_seconds"
        ]
        for database in databases
    }

    scores["ingestion"]["elapsed_seconds"] = (
        lower_is_better_score(
            ingestion_time
        )
    )

    nodes_per_second = {
        database: comparison["ingestion"][database][
            "nodes_per_second"
        ]
        for database in databases
    }

    scores["ingestion"]["nodes_per_second"] = (
        higher_is_better_score(
            nodes_per_second
        )
    )

    relationships_per_second = {
        database: comparison["ingestion"][database][
            "relationships_per_second"
        ]
        for database in databases
    }

    scores["ingestion"]["relationships_per_second"] = (
        higher_is_better_score(
            relationships_per_second
        )
    )

    # ---------------------------------------------------------
    # Query workloads
    # ---------------------------------------------------------
    #
    # Workloads are taken directly from the comparison result.
    # This keeps scoring aligned with the workload registry and
    # avoids maintaining a second hard-coded workload list.
    # ---------------------------------------------------------

    for workload, workload_results in comparison[
        "queries"
    ].items():

        latency_values = {
            database: workload_results[database][
                QUERY_LATENCY_METRIC
            ]
            for database in databases
        }

        qps_values = {
            database: workload_results[database]["qps"]
            for database in databases
        }

        scores["queries"][workload] = {
            "latency": lower_is_better_score(
                latency_values
            ),
            "qps": higher_is_better_score(
                qps_values
            ),
        }

    # ---------------------------------------------------------
    # Overall score
    # ---------------------------------------------------------
    #
    # Equal weighting:
    #
    #   ingestion: 20%
    #   query performance: 80%
    #
    # Query performance is distributed equally across all
    # workloads present in the comparison.
    #
    # Each workload contributes:
    #
    #   50% P95 latency
    #   50% QPS
    #
    # With the current benchmark this means:
    #
    #   point_lookup:       16%
    #   relationship_lookup:16%
    #   traversal_1_hop:    16%
    #   traversal_2_hop:    16%
    #   traversal_3_hop:    16%
    #   aggregation:        16%
    #
    # ---------------------------------------------------------

    workloads = tuple(
        comparison["queries"].keys()
    )

    if not workloads:
        raise ValueError(
            "Cannot calculate scores without query workloads."
        )

    for database in databases:

        ingestion_score = (
            scores["ingestion"]["elapsed_seconds"][
                database
            ]
        )

        query_scores = []

        for workload in workloads:

            latency_score = scores["queries"][
                workload
            ]["latency"][database]

            qps_score = scores["queries"][
                workload
            ]["qps"][database]

            workload_score = (
                latency_score * 0.5
                + qps_score * 0.5
            )

            query_scores.append(
                workload_score
            )

        average_query_score = (
            sum(query_scores)
            / len(query_scores)
        )

        overall_score = (
            ingestion_score * 0.20
            + average_query_score * 0.80
        )

        scores["overall"][database] = {
            "ingestion_score": ingestion_score,
            "query_score": average_query_score,
            "overall_score": overall_score,
        }

    return scores


def print_scores(
    scores: dict[str, Any],
) -> None:

    print()
    print("=" * 90)
    print("NORMALIZED BENCHMARK SCORES")
    print("=" * 90)

    print()
    print(
        f"{'Database':<15}"
        f"{'Ingestion':>15}"
        f"{'Queries':>15}"
        f"{'Overall':>15}"
    )

    print("-" * 90)

    ranked = sorted(
        scores["overall"].items(),
        key=lambda item: item[1]["overall_score"],
        reverse=True,
    )

    for rank, (database, result) in enumerate(
        ranked,
        start=1,
    ):
        print(
            f"{rank}. {database:<11}"
            f"{result['ingestion_score']:>15.4f}"
            f"{result['query_score']:>15.4f}"
            f"{result['overall_score']:>15.4f}"
        )

    print()
    print("Query workload scores")
    print("-" * 90)

    for workload in scores["queries"]:

        print()
        print(workload)

        ranked_workload = []

        for database in scores["databases"]:

            latency = scores["queries"][
                workload
            ]["latency"][database]

            qps = scores["queries"][
                workload
            ]["qps"][database]

            score = (
                latency * 0.5
                + qps * 0.5
            )

            ranked_workload.append(
                (database, score)
            )

        ranked_workload.sort(
            key=lambda item: item[1],
            reverse=True,
        )

        for rank, (database, score) in enumerate(
            ranked_workload,
            start=1,
        ):
            print(
                f"  {rank}. "
                f"{database:<12} "
                f"{score:.4f}"
            )


def save_scores(
    scores: dict[str, Any],
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
            scores,
            file,
            indent=2,
        )


def main() -> None:

    comparison_path = Path(
        "results/comparison.json"
    )

    if not comparison_path.exists():
        raise FileNotFoundError(
            f"Comparison file not found: "
            f"{comparison_path}"
        )

    with comparison_path.open(
        "r",
        encoding="utf-8",
    ) as file:
        comparison = json.load(file)

    scores = build_scores(
        comparison
    )

    print_scores(scores)

    output_path = Path(
        "results/scores.json"
    )

    save_scores(
        scores,
        output_path,
    )

    print()
    print(f"Saved: {output_path}")


if __name__ == "__main__":
    main()