import argparse
from pathlib import Path

from benchmark.config import BenchmarkConfig
from benchmark.database_registry import create_adapter
from benchmark.dataset import get_dataset_counts
from benchmark.metadata_serialization import save_run_metadata
from benchmark.reporter import print_summary
from benchmark.results import BenchmarkSummary
from benchmark.run_directory import create_run_directory
from benchmark.run_metadata import create_run_metadata
from benchmark.runner import run_benchmark
from benchmark.serialization import save_summary
from benchmark.workload_registry import get_workloads


SUPPORTED_DATABASES = [
    "NEO4J",
    "MEMGRAPH",
    "FALKORDB",
    "ARCADEDB",
    "COGNODB",
]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Graph database cloud benchmark"
    )

    parser.add_argument(
        "--database",
        choices=SUPPORTED_DATABASES,
        help="Database to benchmark.",
    )

    parser.add_argument(
        "--all",
        action="store_true",
        help="Benchmark all supported databases.",
    )

    parser.add_argument(
        "--iterations",
        type=int,
        default=100,
        help="Number of measured query iterations.",
    )

    parser.add_argument(
        "--warmup",
        type=int,
        default=10,
        help="Number of warmup query iterations.",
    )

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.database is None and not args.all:
        parser.error(
            "Specify either --database DATABASE or --all."
        )

    if args.database is not None and args.all:
        parser.error(
            "--database and --all cannot be used together."
        )

    config = BenchmarkConfig(
        nodes_path=Path(
            "data/processed/nodes.csv"
        ),
        relationships_path=Path(
            "data/processed/relationships.csv"
        ),
        ingestion_batch_size=1000,
        query_iterations=args.iterations,
        query_warmup_iterations=args.warmup,
        query_seed=42,
    )

    # Discover dataset size dynamically instead of
    # hard-coding node and relationship counts.
    node_count, relationship_count = get_dataset_counts(
        config.nodes_path,
        config.relationships_path,
    )

    # Create a unique directory for this benchmark run.
    metadata = create_run_metadata(
        node_count,
        relationship_count,
        config.ingestion_batch_size,
        config.query_iterations,
        config.query_warmup_iterations,
        config.query_seed,
    )

    run_directory = create_run_directory(
        Path("results"),
        metadata.run_id,
    )

    metadata_path = save_run_metadata(
        metadata,
        run_directory,
    )

    print()
    print("=" * 60)
    print("Benchmark Run")
    print("=" * 60)
    print(f"Run ID:       {metadata.run_id}")
    print(f"Git commit:   {metadata.git_commit}")
    print(f"Run directory: {run_directory}")
    print(f"Metadata:     {metadata_path}")

    if args.all:
        databases = SUPPORTED_DATABASES
    else:
        databases = [args.database]

    for database in databases:
        print()
        print("#" * 60)
        print(f"Running benchmark: {database}")
        print("#" * 60)

        workloads = get_workloads(database)

        adapter = create_adapter(database)

        summary: BenchmarkSummary = run_benchmark(
            adapter,
            config,
            workloads,
        )

        print_summary(summary)

        output_path = save_summary(
            summary,
            run_directory,
        )

        print(f"Saved: {output_path}")


if __name__ == "__main__":
    main()