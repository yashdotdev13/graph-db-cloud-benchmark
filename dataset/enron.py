from pathlib import Path


def normalize_enron(
    input_path: Path,
    output_dir: Path,
) -> tuple[int, int]:
    """
    Normalize the SNAP Enron graph into canonical CSV files.

    The raw SNAP file contains both directions of every undirected
    relationship. We keep only one canonical pair.
    """

    output_dir.mkdir(parents=True, exist_ok=True)

    nodes = set()
    relationships = set()

    with input_path.open("r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()

            if not line or line.startswith("#"):
                continue

            source, target = map(int, line.split())

            nodes.add(source)
            nodes.add(target)

            relationship = (
                min(source, target),
                max(source, target),
            )

            relationships.add(relationship)

    nodes_path = output_dir / "nodes.csv"
    relationships_path = output_dir / "relationships.csv"

    with nodes_path.open("w", encoding="utf-8", newline="") as file:
        file.write("id\n")

        for node_id in sorted(nodes):
            file.write(f"{node_id}\n")

    with relationships_path.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as file:
        file.write("source_id,target_id\n")

        for source, target in sorted(relationships):
            file.write(f"{source},{target}\n")

    return len(nodes), len(relationships)