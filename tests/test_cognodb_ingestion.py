from pathlib import Path

from config.settings import load_database_config
from databases.cognodb import CognoDBAdapter
from benchmark.ingestion import run_ingestion


NODES_PATH = Path("data/processed/nodes.csv")
RELATIONSHIPS_PATH = Path("data/processed/relationships.csv")

EXPECTED_NODES = 36_692
EXPECTED_RELATIONSHIPS = 183_831


def main() -> None:
    config = load_database_config("COGNODB")

    adapter = CognoDBAdapter(config)
    adapter.connect()

    try:
        result = run_ingestion(
            adapter,
            NODES_PATH,
            RELATIONSHIPS_PATH,
            batch_size=1000,
        )

        print(f"Database: {result.database}")
        print(f"Nodes: {result.node_count}")
        print(f"Relationships: {result.relationship_count}")
        print(f"Elapsed: {result.elapsed_seconds:.3f} seconds")
        print(f"Nodes/sec: {result.nodes_per_second:.2f}")
        print(
            "Relationships/sec: "
            f"{result.relationships_per_second:.2f}"
        )

        assert result.node_count == EXPECTED_NODES
        assert result.relationship_count == EXPECTED_RELATIONSHIPS

        print("CognoDB ingestion benchmark: PASS")

    finally:
        adapter.clear()
        adapter.close()


if __name__ == "__main__":
    main()