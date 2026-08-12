import argparse
from pathlib import Path

from benchmark.config import BenchmarkConfig
from benchmark.database_registry import create_adapter
from benchmark.reporter import print_summary
from benchmark.runner import run_benchmark
from benchmark.serialization import save_summary
from benchmark.workload_registry import get_workloads


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Graph database cloud benchmark"
    )

    parser.add_argument(
        "--database",
        choices=[
            "NEO4J",
            "MEMGRAPH",
            "FALKORDB",
            "ARCADEDB",
            "COGNODB",
        ],
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
    )

    if args.all:
        databases = [
            "NEO4J",
            "MEMGRAPH",
            "FALKORDB",
            "ARCADEDB",
            "COGNODB",
        ]
    else:
        databases = [args.database]

    for database in databases:
        print()
        print("#" * 60)
        print(f"Running benchmark: {database}")
        print("#" * 60)

        workloads = get_workloads(database)
        adapter = create_adapter(database)

        summary = run_benchmark(
            adapter,
            config,
            workloads,
        )

        print_summary(summary)

        output_path = save_summary(
            summary,
            Path("results"),
        )

        print(f"Saved: {output_path}")


if __name__ == "__main__":
    main()
