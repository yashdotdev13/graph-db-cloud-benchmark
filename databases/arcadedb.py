import csv
import json
from pathlib import Path
from typing import Any

import requests

from config.settings import DatabaseConfig
from databases.base import GraphDatabaseAdapter


class ArcadeDBAdapter(GraphDatabaseAdapter):
    """
    ArcadeDB adapter using the HTTP API.

    Large-scale ingestion uses ArcadeDB's native HTTP batch endpoint
    instead of issuing one HTTP request per vertex/edge.
    """

    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.session = requests.Session()

        # ArcadeDB batch import requires vertices to be available before
        # edges can reference them.
        self._nodes_path: Path | None = None

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
        language: str = "sql",
    ) -> Any:
        response = self.session.post(
            f"{self.config.uri}{endpoint}",
            auth=(
                self.config.username,
                self.config.password,
            ),
            json={
                "language": language,
                "command": query,
                "params": parameters or {},
            },
            timeout=120,
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
        """
        Remove benchmark data from ArcadeDB.

        Edges are deleted first, followed by benchmark vertices.
        """
        try:
            self.execute(
                "DELETE FROM KNOWS"
            )
        except requests.exceptions.HTTPError:
            # The edge type may not exist yet.
            pass

        try:
            self.execute(
                "DELETE FROM User"
            )
        except requests.exceptions.HTTPError:
            # The vertex type may not exist yet.
            pass

        self._nodes_path = None

    def health_check(self) -> bool:
        try:
            self.connect()
            return True
        except Exception:
            return False

    def prepare_benchmark(self) -> None:
        self.execute(
            """
            CREATE INDEX ON User (id) UNIQUE_HASH
            """
        )

    def load_nodes(
        self,
        path: Path,
        batch_size: int = 1000,
    ) -> int:
        """
        Register the node dataset.

        ArcadeDB's native batch API imports vertices and edges together,
        so the actual bulk import occurs from load_relationships()
        once both canonical CSV paths are available.
        """
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
        Perform one native ArcadeDB batch import containing all
        benchmark vertices followed by all benchmark edges.
        """
        path = Path(path)

        if not path.exists():
            raise FileNotFoundError(
                f"Relationship dataset does not exist: {path}"
            )

        if self._nodes_path is None:
            raise RuntimeError(
                "load_nodes() must be called before "
                "load_relationships() for ArcadeDB bulk ingestion"
            )

        relationship_count = self._count_csv_rows(path)

        self._prepare_schema()

        payload = self._build_batch_payload(
            self._nodes_path,
            path,
        )

        self._run_batch_import(payload)

        return relationship_count

    def _prepare_schema(self) -> None:
        """
        Ensure the benchmark vertex and edge types exist.
        """
        self.execute(
            "CREATE VERTEX TYPE User IF NOT EXISTS"
        )

        self.execute(
            "CREATE EDGE TYPE KNOWS IF NOT EXISTS"
        )

    def _build_batch_payload(
        self,
        nodes_path: Path,
        relationships_path: Path,
    ) -> bytes:
        """
        Build ArcadeDB JSONL batch-import payload.

        Vertices must appear before edges. Temporary IDs allow edges
        to reference vertices created within the same batch operation.
        """
        lines: list[str] = []

        with nodes_path.open(
            "r",
            encoding="utf-8",
            newline="",
        ) as file:
            reader = csv.DictReader(file)

            for row in reader:
                node_id = int(row["id"])

                lines.append(
                    json.dumps(
                        {
                            "@type": "vertex",
                            "@class": "User",
                            "@id": f"u{node_id}",
                            "id": node_id,
                        },
                        separators=(",", ":"),
                    )
                )

        with relationships_path.open(
            "r",
            encoding="utf-8",
            newline="",
        ) as file:
            reader = csv.DictReader(file)

            for row in reader:
                source_id = int(row["source_id"])
                target_id = int(row["target_id"])

                lines.append(
                    json.dumps(
                        {
                            "@type": "edge",
                            "@class": "KNOWS",
                            "@from": f"u{source_id}",
                            "@to": f"u{target_id}",
                        },
                        separators=(",", ":"),
                    )
                )

        return ("\n".join(lines) + "\n").encode("utf-8")

    def _run_batch_import(
        self,
        payload: bytes,
    ) -> None:
        """
        Execute ArcadeDB's native GraphBatch HTTP endpoint.
        """
        endpoint = (
            f"{self.config.uri}"
            f"/api/v1/batch/{self.config.database}"
        )

        response = self.session.post(
            endpoint,
            auth=(
                self.config.username,
                self.config.password,
            ),
            data=payload,
            headers={
                "Content-Type": "application/x-ndjson",
            },
            params={
                "batchSize": 100_000,
                "parallelFlush": "true",
                "preAllocateEdgeChunks": "true",
                "commitEvery": 50_000,
                "expectedEdgeCount": 183_831,
            },
            timeout=300,
        )

        response.raise_for_status()

        result = response.json()

        vertices_created = result.get(
            "verticesCreated",
            0,
        )

        edges_created = result.get(
            "edgesCreated",
            0,
        )

        if vertices_created != 36_692:
            raise RuntimeError(
                "ArcadeDB bulk import created an unexpected "
                f"number of vertices: {vertices_created}"
            )

        if edges_created != 183_831:
            raise RuntimeError(
                "ArcadeDB bulk import created an unexpected "
                f"number of edges: {edges_created}"
            )

    def count_nodes(self) -> int:
        result = self.execute(
            """
            SELECT count(*) AS count
            FROM User
            """
        )

        return self._extract_count(result)

    def count_relationships(self) -> int:
        result = self.execute(
            """
            SELECT count(*) AS count
            FROM KNOWS
            """
        )

        return self._extract_count(result)

    @staticmethod
    def _count_csv_rows(path: Path) -> int:
        with path.open(
            "r",
            encoding="utf-8",
            newline="",
        ) as file:
            reader = csv.reader(file)

            next(reader, None)

            return sum(1 for _ in reader)

    @staticmethod
    def _extract_count(result: Any) -> int:
        """
        Extract count from ArcadeDB's HTTP JSON response.

        Expected shape is typically:

        {
            "result": [
                {
                    "count": 36692
                }
            ]
        }
        """
        records = result.get("result", [])

        if not records:
            return 0

        value = records[0].get("count")

        return int(value)