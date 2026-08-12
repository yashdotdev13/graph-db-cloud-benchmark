from typing import Any
import csv
from pathlib import Path
from neo4j import GraphDatabase

from databases.base import GraphDatabaseAdapter
from config.settings import DatabaseConfig


class Neo4jAdapter(GraphDatabaseAdapter):
    """Neo4j implementation of the common graph database adapter."""

    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.driver = None

    @property
    def name(self) -> str:
        return "neo4j"

    def connect(self) -> None:
        self.driver = GraphDatabase.driver(
            self.config.uri,
            auth=(
                self.config.username,
                self.config.password,
            ),
        )

        self.driver.verify_connectivity()

    def close(self) -> None:
        if self.driver is not None:
            self.driver.close()
            self.driver = None

    def execute(
        self,
        query: str,
        parameters: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        if self.driver is None:
            raise RuntimeError("Neo4j adapter is not connected")

        with self.driver.session(
            database=self.config.database
        ) as session:
            result = session.run(
                query,
                parameters or {},
            )

            return [record.data() for record in result]

    def clear(self) -> None:
        if self.driver is None:
            raise RuntimeError("Neo4j adapter is not connected")

        with self.driver.session(
                database=self.config.database
        ) as session:
            session.run(
                """
                MATCH (n)
                CALL (n) {
                    DETACH DELETE n
                } IN TRANSACTIONS OF 1000 ROWS
                """
            ).consume()

    def health_check(self) -> bool:
        if self.driver is None:
            return False

        try:
            self.driver.verify_connectivity()
            return True
        except Exception:
            return False



    def load_nodes(
        self,
        path: Path,
        batch_size: int = 1000,
    ) -> int:
        if self.driver is None:
            raise RuntimeError("Neo4j adapter is not connected")

        loaded = 0
        batch: list[dict[str, int]] = []

        with path.open(
            "r",
            encoding="utf-8",
            newline="",
        ) as file:
            reader = csv.DictReader(file)

            for row in reader:
                batch.append(
                    {
                        "id": int(row["id"]),
                    }
                )

                if len(batch) >= batch_size:
                    self._load_node_batch(batch)
                    loaded += len(batch)
                    batch.clear()

        if batch:
            self._load_node_batch(batch)
            loaded += len(batch)

        return loaded

    def _load_node_batch(
        self,
        batch: list[dict[str, int]],
    ) -> None:
        with self.driver.session(
            database=self.config.database
        ) as session:
            session.run(
                """
                UNWIND $rows AS row
                CREATE (:User {id: row.id})
                """,
                rows=batch,
            ).consume()

    def load_relationships(
        self,
        path: Path,
        batch_size: int = 1000,
    ) -> int:
        if self.driver is None:
            raise RuntimeError("Neo4j adapter is not connected")

        loaded = 0
        batch: list[dict[str, int]] = []

        with path.open(
            "r",
            encoding="utf-8",
            newline="",
        ) as file:
            reader = csv.DictReader(file)

            for row in reader:
                batch.append(
                    {
                        "source_id": int(row["source_id"]),
                        "target_id": int(row["target_id"]),
                    }
                )

                if len(batch) >= batch_size:
                    self._load_relationship_batch(batch)
                    loaded += len(batch)
                    batch.clear()

        if batch:
            self._load_relationship_batch(batch)
            loaded += len(batch)

        return loaded

    def _load_relationship_batch(
        self,
        batch: list[dict[str, int]],
    ) -> None:
        with self.driver.session(
            database=self.config.database
        ) as session:
            session.run(
                """
                UNWIND $rows AS row
                MATCH (source:User {id: row.source_id})
                MATCH (target:User {id: row.target_id})
                CREATE (source)-[:KNOWS]->(target)
                """,
                rows=batch,
            ).consume()

    def count_nodes(self) -> int:
        result = self.execute(
            "MATCH (n:User) RETURN count(n) AS count"
        )

        return int(result[0]["count"])

    def count_relationships(self) -> int:
        result = self.execute(
            """
            MATCH (:User)-[r:KNOWS]->(:User)
            RETURN count(r) AS count
            """
        )

        return int(result[0]["count"])