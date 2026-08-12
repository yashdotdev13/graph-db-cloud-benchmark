from benchmark.results import BenchmarkSummary


def print_summary(summary: BenchmarkSummary) -> None:
    print()
    print("=" * 60)
    print(f"Database: {summary.database}")
    print("=" * 60)

    ingestion = summary.ingestion

    print("\nIngestion")
    print(f"  Nodes:          {ingestion.node_count}")
    print(f"  Relationships:  {ingestion.relationship_count}")
    print(f"  Elapsed:        {ingestion.elapsed_seconds:.3f} s")
    print(f"  Nodes/sec:      {ingestion.nodes_per_second:.2f}")
    print(
        f"  Relationships/sec: "
        f"{ingestion.relationships_per_second:.2f}"
    )

    print("\nQuery workloads")

    for result in summary.queries:
        print(f"\n  {result.workload}")
        print(f"    Iterations: {result.iterations}")
        print(
            f"    Mean:       "
            f"{result.mean_seconds * 1000:.3f} ms"
        )
        print(
            f"    P50:        "
            f"{result.p50_seconds * 1000:.3f} ms"
        )
        print(
            f"    P95:        "
            f"{result.p95_seconds * 1000:.3f} ms"
        )
        print(
            f"    P99:        "
            f"{result.p99_seconds * 1000:.3f} ms"
        )
        print(
            f"    Max:        "
            f"{result.max_seconds * 1000:.3f} ms"
        )
        print(
            f"    QPS:        "
            f"{result.queries_per_second:.2f}"
        )
