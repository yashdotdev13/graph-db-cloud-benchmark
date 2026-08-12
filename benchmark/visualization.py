import json
from pathlib import Path
from statistics import mean

import matplotlib.pyplot as plt


RESULTS_DIR = Path("results")
PLOTS_DIR = RESULTS_DIR / "plots"

DATABASES = [
    "neo4j",
    "memgraph",
    "falkordb",
    "arcadedb",
    "cognodb",
]

WORKLOADS = [
    "point_lookup",
    "relationship_lookup",
    "traversal",
    "aggregation",
]


def load_json(filename: str):
    path = RESULTS_DIR / filename

    if not path.exists():
        raise FileNotFoundError(
            f"Required result file not found: {path}"
        )

    return json.loads(
        path.read_text(encoding="utf-8")
    )


def load_database_results() -> dict[str, dict]:
    return {
        database: load_json(
            f"{database}.json"
        )
        for database in DATABASES
    }


def get_query(
    result: dict,
    workload: str,
) -> dict:
    for query in result["queries"]:
        if query["workload"] == workload:
            return query

    raise ValueError(
        f"Workload '{workload}' not found "
        f"for {result['database']}"
    )


def percentile(
    values: list[float],
    percentile_value: float,
) -> float:
    values = sorted(values)

    if not values:
        raise ValueError(
            "Cannot calculate percentile of empty data"
        )

    position = (
        percentile_value
        / 100
        * (len(values) - 1)
    )

    lower = int(position)
    upper = min(
        lower + 1,
        len(values) - 1,
    )

    fraction = position - lower

    return (
        values[lower]
        + (
            values[upper]
            - values[lower]
        )
        * fraction
    )


def save_plot(filename: str) -> None:
    PLOTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    plt.tight_layout()

    plt.savefig(
        PLOTS_DIR / filename,
        dpi=200,
        bbox_inches="tight",
    )

    plt.close()

    print(
        f"Saved plot: {PLOTS_DIR / filename}"
    )


def plot_ingestion_throughput(
    results: dict[str, dict],
) -> None:
    nodes_per_second = []
    relationships_per_second = []

    for database in DATABASES:
        ingestion = results[
            database
        ]["ingestion"]

        elapsed = ingestion[
            "elapsed_seconds"
        ]

        nodes_per_second.append(
            ingestion["node_count"]
            / elapsed
        )

        relationships_per_second.append(
            ingestion["relationship_count"]
            / elapsed
        )

    x = range(len(DATABASES))
    width = 0.35

    plt.figure(figsize=(11, 6))

    plt.bar(
        [i - width / 2 for i in x],
        nodes_per_second,
        width,
        label="Nodes/sec",
    )

    plt.bar(
        [i + width / 2 for i in x],
        relationships_per_second,
        width,
        label="Relationships/sec",
    )

    plt.xticks(
        list(x),
        DATABASES,
    )

    plt.ylabel("Operations / second")
    plt.xlabel("Database")
    plt.title(
        "Graph Database Ingestion Throughput"
    )
    plt.legend()

    save_plot(
        "ingestion_throughput.png"
    )


def plot_mean_latency(
    results: dict[str, dict],
) -> None:
    x = range(len(DATABASES))
    width = 0.2

    plt.figure(figsize=(12, 7))

    for index, workload in enumerate(
        WORKLOADS
    ):
        values = []

        for database in DATABASES:
            query = get_query(
                results[database],
                workload,
            )

            mean_latency = (
                query["total_seconds"]
                / query["iterations"]
                * 1000
            )

            values.append(
                mean_latency
            )

        positions = [
            i + (index - 1.5) * width
            for i in x
        ]

        plt.bar(
            positions,
            values,
            width,
            label=workload,
        )

    plt.xticks(
        list(x),
        DATABASES,
    )

    plt.ylabel("Mean Latency (ms)")
    plt.xlabel("Database")
    plt.title(
        "Mean Query Latency"
    )
    plt.legend()

    save_plot(
        "query_mean_latency.png"
    )


def plot_query_percentiles(
    results: dict[str, dict],
) -> None:
    for workload in WORKLOADS:
        p50_values = []
        p95_values = []
        p99_values = []

        for database in DATABASES:
            query = get_query(
                results[database],
                workload,
            )

            latencies = [
                value * 1000
                for value in query[
                    "latencies_seconds"
                ]
            ]

            p50_values.append(
                percentile(
                    latencies,
                    50,
                )
            )

            p95_values.append(
                percentile(
                    latencies,
                    95,
                )
            )

            p99_values.append(
                percentile(
                    latencies,
                    99,
                )
            )

        x = range(len(DATABASES))
        width = 0.25

        plt.figure(figsize=(11, 6))

        plt.bar(
            [i - width for i in x],
            p50_values,
            width,
            label="P50",
        )

        plt.bar(
            x,
            p95_values,
            width,
            label="P95",
        )

        plt.bar(
            [i + width for i in x],
            p99_values,
            width,
            label="P99",
        )

        plt.xticks(
            list(x),
            DATABASES,
        )

        plt.ylabel("Latency (ms)")
        plt.xlabel("Database")
        plt.title(
            f"{workload} Latency Percentiles"
        )
        plt.legend()

        save_plot(
            f"{workload}_percentiles.png"
        )


def plot_query_qps(
    results: dict[str, dict],
) -> None:
    x = range(len(DATABASES))
    width = 0.2

    plt.figure(figsize=(12, 7))

    for index, workload in enumerate(
        WORKLOADS
    ):
        values = []

        for database in DATABASES:
            query = get_query(
                results[database],
                workload,
            )

            qps = (
                query["iterations"]
                / query["total_seconds"]
            )

            values.append(qps)

        positions = [
            i + (index - 1.5) * width
            for i in x
        ]

        plt.bar(
            positions,
            values,
            width,
            label=workload,
        )

    plt.xticks(
        list(x),
        DATABASES,
    )

    plt.ylabel("Queries / second")
    plt.xlabel("Database")
    plt.title(
        "Query Throughput (QPS)"
    )
    plt.legend()

    save_plot(
        "query_qps.png"
    )


def plot_overall_scores() -> None:
    scores = load_json(
        "scores.json"
    )

    overall = scores["overall"]

    databases = list(
        overall.keys()
    )

    values = [
        overall[database][
            "overall_score"
        ]
        for database in databases
    ]

    plt.figure(figsize=(10, 6))

    plt.bar(
        databases,
        values,
    )

    plt.ylabel("Overall Score")
    plt.xlabel("Database")
    plt.title(
        "Overall Benchmark Score"
    )

    save_plot(
        "overall_scores.png"
    )


def plot_tail_latency() -> None:
    tail_analysis = load_json(
        "tail_analysis.json"
    )

    for workload in WORKLOADS:
        entries = [
            entry
            for entry in tail_analysis
            if entry["workload"] == workload
        ]

        entries.sort(
            key=lambda entry:
            DATABASES.index(
                entry["database"]
            )
        )

        databases = [
            entry["database"]
            for entry in entries
        ]

        p99_p50 = [
            entry["p99_p50_ratio"]
            for entry in entries
        ]

        plt.figure(figsize=(10, 6))

        plt.bar(
            databases,
            p99_p50,
        )

        plt.ylabel("P99 / P50")
        plt.xlabel("Database")
        plt.title(
            f"{workload} Tail Latency"
        )

        save_plot(
            f"{workload}_tail_latency.png"
        )


def main() -> None:
    print(
        "=" * 70
    )
    print(
        "GRAPH DATABASE BENCHMARK VISUALIZATION"
    )
    print(
        "=" * 70
    )

    results = load_database_results()

    print("\nGenerating ingestion chart...")
    plot_ingestion_throughput(
        results
    )

    print("\nGenerating mean latency chart...")
    plot_mean_latency(
        results
    )

    print("\nGenerating percentile charts...")
    plot_query_percentiles(
        results
    )

    print("\nGenerating QPS chart...")
    plot_query_qps(
        results
    )

    print("\nGenerating overall score chart...")
    plot_overall_scores()

    print("\nGenerating tail-latency charts...")
    plot_tail_latency()

    print("\n" + "=" * 70)
    print(
        f"All charts saved to: {PLOTS_DIR}"
    )
    print("=" * 70)


if __name__ == "__main__":
    main()
