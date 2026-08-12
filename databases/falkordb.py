import csv
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any

import redis

from config.settings import DatabaseConfig
from databases.base import GraphDatabaseAdapter


class FalkorDBAdapter(GraphDatabaseAdapter):
    """
    FalkorDB adapter using the Redis protocol and the official
    falkordb-bulk-loader for large-scale dataset ingestion.
    """

    GRAPH_NAME = "benchmark"

    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.client: redis.Redis | None = None

        # The bulk loader needs both files at the same time.
        # load_nodes() records the node file and load_relationships()
        # performs the actual bulk import once both paths are known.
        self._nodes_path: Path | None = None

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

        # FalkorDB GRAPH.QUERY does not currently use the
        # parameters argument in this adapter.
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

        try:
            self.client.execute_command(
                "GRAPH.DELETE",
                self.GRAPH_NAME,
            )
        except redis.exceptions.ResponseError as exc:
            # FalkorDB returns an error when GRAPH.DELETE is called
            # for a graph that does not exist yet.
            message = str(exc).lower()

            if (
                "empty key" not in message
                and "not found" not in message
                and "does not exist" not in message
            ):
                raise

        self._nodes_path = None

    def health_check(self) -> bool:
        if self.client is None:
            return False

        try:
            self.client.ping()
            return True
        except Exception:
            return False

    def load_nodes(
        self,
        path: Path,
        batch_size: int = 1000,
    ) -> int:
        """
        Register the canonical node CSV for the FalkorDB bulk loader.

        FalkorDB's official bulk loader requires nodes and relationships
        together, so the actual import is performed by load_relationships()
        once both files are known.

        batch_size is accepted to satisfy the common adapter interface.
        The official FalkorDB bulk loader manages its own buffering.
        """
        if self.client is None:
            raise RuntimeError(
                "FalkorDB adapter is not connected"
            )

        path = Path(path)

        if not path.exists():
            raise FileNotFoundError(
                f"Node dataset does not exist: {path}"
            )

        self._nodes_path = path

        return self._count_csv_rows(path)

    def load_relationships(
        self,
        path: Path,
        batch_size: int = 1000,
    ) -> int:
        """
        Bulk-load the canonical nodes and relationships using the
        official falkordb-bulk-insert CLI.

        The bulk loader performs the entire graph ingestion as one
        operation, which is significantly more efficient than issuing
        thousands of individual Cypher statements.
        """
        if self.client is None:
            raise RuntimeError(
                "FalkorDB adapter is not connected"
            )

        path = Path(path)

        if not path.exists():
            raise FileNotFoundError(
                f"Relationship dataset does not exist: {path}"
            )

        if self._nodes_path is None:
            raise RuntimeError(
                "load_nodes() must be called before "
                "load_relationships() for FalkorDB bulk ingestion"
            )

        relationship_count = self._count_csv_rows(path)

        self._run_bulk_loader(
            nodes_path=self._nodes_path,
            relationships_path=path,
        )

        return relationship_count

    def _run_bulk_loader(
        self,
        nodes_path: Path,
        relationships_path: Path,
    ) -> None:
        """
        Invoke the official FalkorDB bulk loader.

        We intentionally invoke the CLI instead of importing its internal
        Click command because the CLI is the supported public entry point
        of falkordb-bulk-loader.
        """
        executable = shutil.which("falkordb-bulk-insert")

        if executable is None:
            raise RuntimeError(
                "falkordb-bulk-insert executable was not found. "
                "Install it with: "
                "pip install falkordb-bulk-loader"
            )

        command = [
            executable,
            self.GRAPH_NAME,
            "-u",
            self.config.uri,
            "-N",
            "User",
            str(nodes_path),
            "-R",
            "KNOWS",
            str(relationships_path),
            "-j",
            "INTEGER",
            "-i",
            "User:id",
        ]

        # The official loader uses stdout/stderr for progress and
        # diagnostic information. Keep it visible so benchmark failures
        # are easy to diagnose.
        result = subprocess.run(
            command,
            check=False,
            text=True,
            env=os.environ.copy(),
        )

        if result.returncode != 0:
            raise RuntimeError(
                "FalkorDB bulk ingestion failed "
                f"with exit code {result.returncode}"
            )

    def count_nodes(self) -> int:
        result = self.execute(
            """
            MATCH (n:User)
            RETURN count(n)
            """
        )

        return int(result[1][0][0])

    def count_relationships(self) -> int:
        result = self.execute(
            """
            MATCH ()-[r:KNOWS]->()
            RETURN count(r)
            """
        )

        return int(result[1][0][0])

    @staticmethod
    def _count_csv_rows(path: Path) -> int:
        """
        Count data rows in a CSV file without loading the entire file
        into memory.
        """
        with path.open(
            "r",
            encoding="utf-8",
            newline="",
        ) as file:
            reader = csv.reader(file)

            # Skip header.
            next(reader, None)

            return sum(1 for _ in reader)