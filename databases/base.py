from abc import ABC, abstractmethod
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
    def execute(self, query: str, parameters: dict[str, Any] | None = None) -> Any:
        """
        Execute a database query.

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

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the canonical database name."""
        raise NotImplementedError