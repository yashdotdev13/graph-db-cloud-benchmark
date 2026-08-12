from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class BenchmarkWorkload:
    """
    Defines one benchmark operation.

    A workload represents a logical operation that should have
    equivalent semantics across all supported graph databases.
    """

    name: str
    description: str
    query: str
    parameters: dict[str, Any] | None = None
    result_limit: int | None = None