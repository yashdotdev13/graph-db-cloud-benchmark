from dataclasses import dataclass
from datetime import datetime, timezone
import platform
import sys

from benchmark.git import get_git_commit


@dataclass(frozen=True)
class RunMetadata:
    run_id: str
    timestamp_utc: str
    git_commit: str
    python_version: str
    platform: str
    processor: str
    node_count: int
    relationship_count: int
    ingestion_batch_size: int
    query_iterations: int
    query_warmup_iterations: int
    query_seed: int


def generate_run_id() -> str:
    return datetime.now(timezone.utc).strftime(
        "%Y%m%dT%H%M%SZ"
    )


def create_run_metadata(
    node_count: int,
    relationship_count: int,
    ingestion_batch_size: int,
    query_iterations: int,
    query_warmup_iterations: int,
    query_seed: int,
) -> RunMetadata:
    timestamp = datetime.now(timezone.utc)

    return RunMetadata(
        run_id=timestamp.strftime("%Y%m%dT%H%M%SZ"),
        timestamp_utc=timestamp.isoformat(),
        git_commit=get_git_commit(),
        python_version=sys.version,
        platform=platform.platform(),
        processor=platform.processor(),
        node_count=node_count,
        relationship_count=relationship_count,
        ingestion_batch_size=ingestion_batch_size,
        query_iterations=query_iterations,
        query_warmup_iterations=query_warmup_iterations,
        query_seed=query_seed,
    )