from typing import Any

from neo4j import GraphDatabase

from config.settings import DatabaseConfig
from databases.base import GraphDatabaseAdapter


class MemgraphAdapter(GraphDatabaseAdapter):
    """Memgraph implementation using the Neo4j-compatible Bolt protocol."""

    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.driver = None

    @property
    def name(self) -> str:
        return "memgraph"

    def connect(self) -> None:
        self.driver = GraphDatabase.driver(
            self.config.uri,
            auth=(
                self.config.username,
                self.config.password,
            )
            if self.config.username
            else None,
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
            raise RuntimeError("Memgraph adapter is not connected")

        with self.driver.session() as session:
            result = session.run(
                query,
                parameters or {},
            )

            return [record.data() for record in result]

    def clear(self) -> None:
        self.execute(
            "MATCH (n) DETACH DELETE n"
        )

    def health_check(self) -> bool:
        if self.driver is None:
            return False

        try:
            self.driver.verify_connectivity()
            return True
        except Exception:
            return False