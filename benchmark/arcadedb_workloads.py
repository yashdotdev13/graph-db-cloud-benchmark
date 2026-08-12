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


TRAVERSAL_1_HOP = BenchmarkWorkload(
    name="traversal_1_hop",
    description="Traverse KNOWS relationships exactly one hop.",
    query="""
SELECT FROM (
    TRAVERSE out("KNOWS")
    FROM (
        SELECT FROM User
        WHERE id = :id
    )
    MAXDEPTH 1
)
WHERE $depth = 1
""",
    parameters={"id": 0},
    result_limit=1000,
)


TRAVERSAL_2_HOP = BenchmarkWorkload(
    name="traversal_2_hop",
    description="Traverse KNOWS relationships exactly two hops.",
    query="""
SELECT FROM (
    TRAVERSE out("KNOWS")
    FROM (
        SELECT FROM User
        WHERE id = :id
    )
    MAXDEPTH 2
)
WHERE $depth = 2
""",
    parameters={"id": 0},
    result_limit=1000,
)


TRAVERSAL_3_HOP = BenchmarkWorkload(
    name="traversal_3_hop",
    description="Traverse KNOWS relationships exactly three hops.",
    query="""
SELECT FROM (
    TRAVERSE out("KNOWS")
    FROM (
        SELECT FROM User
        WHERE id = :id
    )
    MAXDEPTH 3
)
WHERE $depth = 3
""",
    parameters={"id": 0},
    result_limit=1000,
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
    TRAVERSAL_1_HOP,
    TRAVERSAL_2_HOP,
    TRAVERSAL_3_HOP,
    AGGREGATION,
)