from typing import Any

import requests

from config.settings import DatabaseConfig
from databases.base import GraphDatabaseAdapter


class ArcadeDBAdapter(GraphDatabaseAdapter):
    """ArcadeDB implementation using the HTTP API."""

    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.session = requests.Session()

    @property
    def name(self) -> str:
        return "arcadedb"

    def connect(self) -> None:
        response = self.session.get(
            f"{self.config.uri}/api/v1/server",
            params={"mode": "basic"},
            auth=(
                self.config.username,
                self.config.password,
            ),
            timeout=10,
        )

        response.raise_for_status()

    def close(self) -> None:
        self.session.close()

    def _request(
        self,
        endpoint: str,
        query: str,
        parameters: dict[str, Any] | None = None,
    ) -> Any:
        response = self.session.post(
            f"{self.config.uri}{endpoint}",
            auth=(
                self.config.username,
                self.config.password,
            ),
            json={
                "language": "sql",
                "command": query,
                "params": parameters or {},
            },
            timeout=30,
        )

        response.raise_for_status()

        return response.json()

    def execute(
        self,
        query: str,
        parameters: dict[str, Any] | None = None,
    ) -> Any:
        normalized = query.strip().upper()

        read_commands = (
            "SELECT",
            "MATCH",
            "TRAVERSE",
            "EXPLAIN",
        )

        if normalized.startswith(read_commands):
            endpoint = (
                f"/api/v1/query/"
                f"{self.config.database}"
            )
        else:
            endpoint = (
                f"/api/v1/command/"
                f"{self.config.database}"
            )

        return self._request(
            endpoint,
            query,
            parameters,
        )

    def clear(self) -> None:
        self.execute(
            "DELETE VERTEX FROM User"
        )

    def health_check(self) -> bool:
        try:
            self.connect()
            return True
        except Exception:
            return False