from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


class GraphDatabaseAdapter(ABC):
    """
    Common interface implemented by every graph database adapter.
    """

    @abstractmethod
    def connect(self) -> None:
        """Establish a connection to the database."""
        raise NotImplementedError

    @abstractmethod
    def close(self) -> None:
        """Close the database connection."""
        raise NotImplementedError

    @abstractmethod
    def execute(
        self,
        query: str,
        parameters: dict[str, Any] | None = None,
    ) -> Any:
        """
        Execute a database-specific query.

        Parameters:
            query: Database-specific query string.
            parameters: Optional query parameters.
        """
        raise NotImplementedError

    @abstractmethod
    def clear(self) -> None:
        """Remove benchmark data from the database."""
        raise NotImplementedError

    @abstractmethod
    def health_check(self) -> bool:
        """Return True if the database is reachable and healthy."""
        raise NotImplementedError

    @abstractmethod
    def load_nodes(
        self,
        path: Path,
        batch_size: int = 1000,
    ) -> int:
        """
        Load nodes from the canonical nodes.csv dataset.

        Returns:
            Number of nodes loaded.
        """
        raise NotImplementedError

    @abstractmethod
    def load_relationships(
        self,
        path: Path,
        batch_size: int = 1000,
    ) -> int:
        """
        Load relationships from the canonical relationships.csv dataset.

        Returns:
            Number of relationships loaded.
        """
        raise NotImplementedError

    @abstractmethod
    def count_nodes(self) -> int:
        """Return the number of benchmark nodes currently stored."""
        raise NotImplementedError

    @abstractmethod
    def count_relationships(self) -> int:
        """Return the number of benchmark relationships currently stored."""
        raise NotImplementedError

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the canonical database name."""
        raise NotImplementedError