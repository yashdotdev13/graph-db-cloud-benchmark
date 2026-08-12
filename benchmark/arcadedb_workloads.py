from benchmark.workload import BenchmarkWorkload


POINT_LOOKUP = BenchmarkWorkload(
    name="point_lookup",
    description="Lookup a single user by ID.",
    query="""
SELECT FROM User
WHERE id = :id
""",
    parameters={"id": 0},
)


RELATIONSHIP_LOOKUP = BenchmarkWorkload(
    name="relationship_lookup",
    description="Find direct KNOWS relationships for a user.",
    query="""
SELECT out("KNOWS")
FROM User
WHERE id = :id
""",
    parameters={"id": 0},
)


TRAVERSAL = BenchmarkWorkload(
    name="traversal",
    description="Traverse KNOWS relationships up to three hops.",
    query="""
SELECT FROM (
    TRAVERSE out("KNOWS")
    FROM (
        SELECT FROM User
        WHERE id = :id
    )
    MAXDEPTH 3
)
WHERE $depth >= 1
""",
    parameters={"id": 0},
)


AGGREGATION = BenchmarkWorkload(
    name="aggregation",
    description="Count all users.",
    query="""
SELECT count(*) AS count
FROM User
""",
)


ALL_WORKLOADS = (
    POINT_LOOKUP,
    RELATIONSHIP_LOOKUP,
    TRAVERSAL,
    AGGREGATION,
)
