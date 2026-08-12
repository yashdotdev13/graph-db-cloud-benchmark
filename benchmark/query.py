from dataclasses import dataclass
from random import Random
from statistics import mean
from time import perf_counter
from typing import Any

from benchmark.workload import BenchmarkWorkload
from databases.base import GraphDatabaseAdapter


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


def _generate_node_ids(
    count: int,
    node_count: int,
    seed: int,
) -> list[int]:
    if count <= 0:
        return []

    if node_count <= 0:
        raise ValueError(
            "node_count must be greater than zero"
        )

    random = Random(seed)

    return [
        random.randrange(node_count)
        for _ in range(count)
    ]


def _build_parameters(
    workload: BenchmarkWorkload,
    node_id: int | None,
) -> dict[str, Any]:
    parameters = dict(
        workload.parameters or {}
    )

    if "id" in parameters and node_id is not None:
        parameters["id"] = node_id

    return parameters


def run_query_benchmark(
    adapter: GraphDatabaseAdapter,
    workload: BenchmarkWorkload,
    iterations: int = 100,
    warmup_iterations: int = 10,
    node_count: int | None = None,
    query_seed: int = 42,
) -> QueryBenchmarkResult:
    """
    Execute one workload and measure query latency.

    Warmup executions are excluded from measurements.

    Workloads containing an ``id`` parameter receive deterministic
    node IDs generated from ``query_seed``. The same seed and
    iteration count therefore produce the same query sequence
    across benchmark runs and databases.
    """

    if iterations <= 0:
        raise ValueError(
            "iterations must be greater than zero"
        )

    if warmup_iterations < 0:
        raise ValueError(
            "warmup_iterations cannot be negative"
        )

    requires_node_id = (
        workload.parameters is not None
        and "id" in workload.parameters
    )

    if requires_node_id and node_count is None:
        raise ValueError(
            "node_count is required for workloads "
            "that use an id parameter"
        )

    total_ids = (
        warmup_iterations + iterations
        if requires_node_id
        else 0
    )

    node_ids = _generate_node_ids(
        count=total_ids,
        node_count=node_count or 0,
        seed=query_seed,
    )

    warmup_ids = node_ids[:warmup_iterations]
    measurement_ids = node_ids[warmup_iterations:]

    # Warmup phase.
    for index in range(warmup_iterations):
        node_id = (
            warmup_ids[index]
            if requires_node_id
            else None
        )

        parameters = _build_parameters(
            workload,
            node_id,
        )

        adapter.execute(
            workload.query,
            parameters,
        )

    # Measurement phase.
    latencies: list[float] = []

    start_total = perf_counter()

    for index in range(iterations):
        node_id = (
            measurement_ids[index]
            if requires_node_id
            else None
        )

        parameters = _build_parameters(
            workload,
            node_id,
        )

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