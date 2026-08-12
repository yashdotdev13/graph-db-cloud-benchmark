from dataclasses import dataclass


@dataclass(frozen=True)
class BenchmarkWorkload:
    """
    Defines one benchmark operation.
    """

    name: str
    description: str
    query: str