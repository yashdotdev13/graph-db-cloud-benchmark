from typing import Any

import redis

from config.settings import DatabaseConfig
from databases.base import GraphDatabaseAdapter


class FalkorDBAdapter(GraphDatabaseAdapter):
    """FalkorDB implementation using Redis protocol."""

    GRAPH_NAME = "benchmark"

    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.client: redis.Redis | None = None

    @property
    def name(self) -> str:
        return "falkordb"

    def connect(self) -> None:
        self.client = redis.Redis.from_url(
            self.config.uri,
            decode_responses=True,
        )

        self.client.ping()

    def close(self) -> None:
        if self.client is not None:
            self.client.close()
            self.client = None

    def execute(
        self,
        query: str,
        parameters: dict[str, Any] | None = None,
    ) -> Any:
        if self.client is None:
            raise RuntimeError(
                "FalkorDB adapter is not connected"
            )

        return self.client.execute_command(
            "GRAPH.QUERY",
            self.GRAPH_NAME,
            query,
        )

    def clear(self) -> None:
        if self.client is None:
            raise RuntimeError(
                "FalkorDB adapter is not connected"
            )

        self.client.execute_command(
            "GRAPH.DELETE",
            self.GRAPH_NAME,
        )

    def health_check(self) -> bool:
        if self.client is None:
            return False

        try:
            self.client.ping()
            return True
        except Exception:
            return False