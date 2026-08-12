from dataclasses import dataclass
from statistics import mean
from time import perf_counter

from databases.base import GraphDatabaseAdapter
from benchmark.workload import BenchmarkWorkload


@dataclass(frozen=True)
class QueryBenchmarkResult:
    database: str
    workload: str
    iterations: int
    warmup_iterations: int
    total_seconds: float
    latencies_seconds: tuple[float, ...]

    @property
    def min_seconds(self) -> float:
        return min(self.latencies_seconds)

    @property
    def max_seconds(self) -> float:
        return max(self.latencies_seconds)

    @property
    def mean_seconds(self) -> float:
        return mean(self.latencies_seconds)

    @property
    def p50_seconds(self) -> float:
        return self._percentile(50)

    @property
    def p95_seconds(self) -> float:
        return self._percentile(95)

    @property
    def p99_seconds(self) -> float:
        return self._percentile(99)

    @property
    def queries_per_second(self) -> float:
        return self.iterations / self.total_seconds

    def _percentile(self, percentile: float) -> float:
        values = sorted(self.latencies_seconds)

        if len(values) == 1:
            return values[0]

        position = (
            percentile / 100
        ) * (len(values) - 1)

        lower = int(position)
        upper = lower + 1

        if upper >= len(values):
            return values[lower]

        weight = position - lower

        return (
            values[lower]
            + (values[upper] - values[lower]) * weight
        )


def run_query_benchmark(
    adapter: GraphDatabaseAdapter,
    workload: BenchmarkWorkload,
    iterations: int = 100,
    warmup_iterations: int = 10,
) -> QueryBenchmarkResult:
    """
    Execute one workload and measure query latency.

    Warmup executions are excluded from measurements.
    """

    if iterations <= 0:
        raise ValueError(
            "iterations must be greater than zero"
        )

    if warmup_iterations < 0:
        raise ValueError(
            "warmup_iterations cannot be negative"
        )

    parameters = workload.parameters or {}

    # Warmup phase.
    for _ in range(warmup_iterations):
        adapter.execute(
            workload.query,
            parameters,
        )

    # Measurement phase.
    latencies: list[float] = []

    start_total = perf_counter()

    for _ in range(iterations):
        start = perf_counter()

        adapter.execute(
            workload.query,
            parameters,
        )

        elapsed = perf_counter() - start
        latencies.append(elapsed)

    total_seconds = perf_counter() - start_total

    return QueryBenchmarkResult(
        database=adapter.name,
        workload=workload.name,
        iterations=iterations,
        warmup_iterations=warmup_iterations,
        total_seconds=total_seconds,
        latencies_seconds=tuple(latencies),
    )