import json
from dataclasses import asdict
from pathlib import Path

from benchmark.run_metadata import RunMetadata


def save_run_metadata(
    metadata: RunMetadata,
    run_directory: Path,
) -> Path:
    output_path = run_directory / "metadata.json"

    output_path.write_text(
        json.dumps(
            asdict(metadata),
            indent=2,
        ),
        encoding="utf-8",
    )

    return output_path
