from pathlib import Path


def create_run_directory(
    output_root: Path,
    run_id: str,
) -> Path:
    run_directory = output_root / "runs" / run_id

    run_directory.mkdir(
        parents=True,
        exist_ok=False,
    )

    return run_directory
