from pathlib import Path
import csv


def validate_processed_dataset(data_dir: Path) -> None:
    nodes_path = data_dir / "nodes.csv"
    relationships_path = data_dir / "relationships.csv"

    if not nodes_path.exists():
        raise FileNotFoundError(nodes_path)

    if not relationships_path.exists():
        raise FileNotFoundError(relationships_path)

    nodes: set[int] = set()

    with nodes_path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)

        if reader.fieldnames != ["id"]:
            raise ValueError(
                f"Invalid nodes.csv header: {reader.fieldnames}"
            )

        for row in reader:
            node_id = int(row["id"])

            if node_id in nodes:
                raise ValueError(f"Duplicate node ID: {node_id}")

            nodes.add(node_id)

    relationships: set[tuple[int, int]] = set()

    with relationships_path.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as file:
        reader = csv.DictReader(file)

        expected = ["source_id", "target_id"]

        if reader.fieldnames != expected:
            raise ValueError(
                f"Invalid relationships.csv header: {reader.fieldnames}"
            )

        for row in reader:
            source = int(row["source_id"])
            target = int(row["target_id"])

            if source == target:
                raise ValueError(
                    f"Self-loop detected: {source}"
                )

            if source not in nodes:
                raise ValueError(
                    f"Unknown source node: {source}"
                )

            if target not in nodes:
                raise ValueError(
                    f"Unknown target node: {target}"
                )

            if source > target:
                raise ValueError(
                    f"Relationship is not canonical: {source},{target}"
                )

            relationship = (source, target)

            if relationship in relationships:
                raise ValueError(
                    f"Duplicate relationship: {source},{target}"
                )

            relationships.add(relationship)

    print(f"Nodes: {len(nodes)}")
    print(f"Relationships: {len(relationships)}")
    print("Self-loops: 0")
    print("Dataset validation: PASS")