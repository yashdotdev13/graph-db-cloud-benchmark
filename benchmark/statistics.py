from dataclasses import dataclass
from statistics import stdev

from benchmark.query import QueryBenchmarkResult


@dataclass(frozen=True)
class QueryStatistics:
    database: str
    workload: str
    mean_seconds: float
    min_seconds: float
    max_seconds: float
    p50_seconds: float
    p95_seconds: float
    p99_seconds: float
    standard_deviation_seconds: float
    coefficient_of_variation: float
    p99_p50_ratio: float


def calculate_query_statistics(
    result: QueryBenchmarkResult,
) -> QueryStatistics:
    latencies = result.latencies_seconds

    if not latencies:
        raise ValueError(
            "Cannot calculate statistics without latency samples."
        )

    standard_deviation = (
        stdev(latencies)
        if len(latencies) > 1
        else 0.0
    )

    coefficient_of_variation = (
        standard_deviation / result.mean_seconds
        if result.mean_seconds > 0
        else 0.0
    )

    p99_p50_ratio = (
        result.p99_seconds / result.p50_seconds
        if result.p50_seconds > 0
        else 0.0
    )

    return QueryStatistics(
        database=result.database,
        workload=result.workload,
        mean_seconds=result.mean_seconds,
        min_seconds=result.min_seconds,
        max_seconds=result.max_seconds,
        p50_seconds=result.p50_seconds,
        p95_seconds=result.p95_seconds,
        p99_seconds=result.p99_seconds,
        standard_deviation_seconds=standard_deviation,
        coefficient_of_variation=coefficient_of_variation,
        p99_p50_ratio=p99_p50_ratio,
    )
