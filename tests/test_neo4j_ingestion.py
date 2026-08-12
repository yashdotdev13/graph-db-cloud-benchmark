from pathlib import Path

from config.settings import load_database_config
from databases.neo4j import Neo4jAdapter
from benchmark.ingestion import run_ingestion


NODES_PATH = Path("data/processed/nodes.csv")
RELATIONSHIPS_PATH = Path("data/processed/relationships.csv")


def main() -> None:
    config = load_database_config(
        "NEO4J",
        database="neo4j",
    )

    adapter = Neo4jAdapter(config)

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

        assert result.node_count == 36_692
        assert result.relationship_count == 183_831

        print("Neo4j ingestion benchmark: PASS")

    finally:
        adapter.clear()
        adapter.close()


if __name__ == "__main__":
    main()