from pathlib import Path

from config.settings import load_database_config
from databases.arcadedb import ArcadeDBAdapter


NODES_PATH = Path("data/processed/nodes.csv")
RELATIONSHIPS_PATH = Path("data/processed/relationships.csv")

EXPECTED_NODES = 36_692
EXPECTED_RELATIONSHIPS = 183_831


def main() -> None:
    config = load_database_config("ARCADEDB")

    adapter = ArcadeDBAdapter(config)
    adapter.connect()

    try:
        print("1. Clearing database...")
        adapter.clear()

        print("2. Loading nodes...")
        loaded_nodes = adapter.load_nodes(
            NODES_PATH,
            batch_size=1000,
        )
        print(f"   Nodes loaded: {loaded_nodes}")

        print("3. Loading relationships...")
        loaded_relationships = adapter.load_relationships(
            RELATIONSHIPS_PATH,
            batch_size=1000,
        )
        print(
            f"   Relationships loaded: "
            f"{loaded_relationships}"
        )

        print("4. Verifying counts...")

        node_count = adapter.count_nodes()
        relationship_count = adapter.count_relationships()

        print(f"   Node count: {node_count}")
        print(
            f"   Relationship count: "
            f"{relationship_count}"
        )

        assert loaded_nodes == EXPECTED_NODES
        assert loaded_relationships == EXPECTED_RELATIONSHIPS
        assert node_count == EXPECTED_NODES
        assert relationship_count == EXPECTED_RELATIONSHIPS

        print("5. ArcadeDB loading: PASS")

    finally:
        adapter.clear()
        adapter.close()


if __name__ == "__main__":
    main()