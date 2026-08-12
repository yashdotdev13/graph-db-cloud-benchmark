import csv
from pathlib import Path
from typing import Any

from neo4j import GraphDatabase

from config.settings import DatabaseConfig
from databases.base import GraphDatabaseAdapter


class CognoDBAdapter(GraphDatabaseAdapter):
    """
    CognoDB adapter using the Neo4j-compatible Bolt protocol.
    """

    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.driver = None

    @property
    def name(self) -> str:
        return "cognodb"

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
    ) -> Any:
        if self.driver is None:
            raise RuntimeError(
                "CognoDB adapter is not connected"
            )

        with self.driver.session(
            database=self.config.database
        ) as session:
            result = session.run(
                query,
                parameters or {},
            )

            return result.data()

    def clear(self) -> None:
        if self.driver is None:
            raise RuntimeError(
                "CognoDB adapter is not connected"
            )

        while True:
            result = self.execute(
                """
                MATCH (n)
                RETURN count(n) AS count
                """
            )

            count = result[0]["count"]

            if count == 0:
                break

            self.execute(
                """
                MATCH (n)
                WITH n
                LIMIT 1000
                DETACH DELETE n
                """
            )

    def health_check(self) -> bool:
        try:
            if self.driver is None:
                self.connect()

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
            raise RuntimeError(
                "CognoDB adapter is not connected"
            )

        total = 0
        batch: list[dict[str, Any]] = []

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
                    total += len(batch)
                    batch.clear()

            if batch:
                self._load_node_batch(batch)
                total += len(batch)

        return total

    def _load_node_batch(
        self,
        batch: list[dict[str, Any]],
    ) -> None:
        self.execute(
            """
            UNWIND $rows AS row
            CREATE (:User {id: row.id})
            """,
            {"rows": batch},
        )

    def load_relationships(
        self,
        path: Path,
        batch_size: int = 1000,
    ) -> int:
        if self.driver is None:
            raise RuntimeError(
                "CognoDB adapter is not connected"
            )

        total = 0
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
                    total += len(batch)
                    batch.clear()

            if batch:
                self._load_relationship_batch(batch)
                total += len(batch)

        return total

    def _load_relationship_batch(
        self,
        batch: list[dict[str, int]],
    ) -> None:
        self.execute(
            """
            UNWIND $rows AS row
            MATCH (source:User {id: row.source_id})
            MATCH (target:User {id: row.target_id})
            CREATE (source)-[:KNOWS]->(target)
            """,
            {"rows": batch},
        )

    def count_nodes(self) -> int:
        result = self.execute(
            """
            MATCH (n:User)
            RETURN count(n) AS count
            """
        )

        return result[0]["count"]

    def count_relationships(self) -> int:
        result = self.execute(
            """
            MATCH ()-[r:KNOWS]->()
            RETURN count(r) AS count
            """
        )

        return result[0]["count"]