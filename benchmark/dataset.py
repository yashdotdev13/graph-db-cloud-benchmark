import csv
from pathlib import Path


def count_csv_rows(path: Path) -> int:
    with path.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as file:
        reader = csv.reader(file)

        next(reader, None)

        return sum(1 for _ in reader)


def get_dataset_counts(
    nodes_path: Path,
    relationships_path: Path,
) -> tuple[int, int]:
    node_count = count_csv_rows(nodes_path)
    relationship_count = count_csv_rows(
        relationships_path
    )

    return node_count, relationship_count
