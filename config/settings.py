from dataclasses import dataclass
import os


@dataclass(frozen=True)
class DatabaseConfig:
    uri: str
    username: str | None = None
    password: str | None = None
    database: str | None = None


def load_database_config(
    prefix: str,
    *,
    database: str | None = None,
) -> DatabaseConfig:
    """
    Load database connection configuration from environment variables.

    Example:
        prefix="NEO4J"

    reads:
        NEO4J_URI
        NEO4J_USERNAME
        NEO4J_PASSWORD
    """

    uri = os.getenv(f"{prefix}_URI")

    if not uri:
        raise RuntimeError(
            f"{prefix}_URI is not configured"
        )

    return DatabaseConfig(
        uri=uri,
        username=os.getenv(f"{prefix}_USERNAME"),
        password=os.getenv(f"{prefix}_PASSWORD"),
        database=database or os.getenv(f"{prefix}_DATABASE"),
    )