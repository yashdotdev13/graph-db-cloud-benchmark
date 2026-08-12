import json
from dataclasses import asdict
from pathlib import Path

from benchmark.results import BenchmarkSummary


def save_summary(
    summary: BenchmarkSummary,
    output_dir: Path,
) -> Path:
    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = (
        output_dir / f"{summary.database}.json"
    )

    data = asdict(summary)

    output_path.write_text(
        json.dumps(
            data,
            indent=2,
        ),
        encoding="utf-8",
    )

    return output_path
