from benchmark.workload import BenchmarkWorkload


POINT_LOOKUP = BenchmarkWorkload(
    name="point_lookup",
    description="Lookup a single user by ID.",
    query="""
MATCH (u:User {id: $id})
RETURN u
""",
    parameters={"id": 0},
)

INDEXED_LOOKUP = BenchmarkWorkload(
    name="indexed_lookup",
    description="Lookup a user by the indexed id property.",
    query="""
MATCH (u:User)
WHERE u.id = $id
RETURN u
""",
    parameters={"id": 0},
)


RELATIONSHIP_LOOKUP = BenchmarkWorkload(
    name="relationship_lookup",
    description="Find direct relationships for a user.",
    query="""
MATCH (u:User {id: $id})-[:KNOWS]->(friend)
RETURN friend
""",
    parameters={"id": 0},
)


TRAVERSAL_1_HOP = BenchmarkWorkload(
    name="traversal_1_hop",
    description="Traverse KNOWS relationships exactly one hop.",
    query="""
MATCH (u:User {id: $id})-[:KNOWS]->(friend)
RETURN friend
""",
    parameters={"id": 0},
    result_limit=1000,
)


TRAVERSAL_2_HOP = BenchmarkWorkload(
    name="traversal_2_hop",
    description="Traverse KNOWS relationships exactly two hops.",
    query="""
MATCH (u:User {id: $id})-[:KNOWS*2]->(friend)
RETURN friend
""",
    parameters={"id": 0},
    result_limit=1000,
)


TRAVERSAL_3_HOP = BenchmarkWorkload(
    name="traversal_3_hop",
    description="Traverse KNOWS relationships exactly three hops.",
    query="""
MATCH (u:User {id: $id})-[:KNOWS*3]->(friend)
RETURN friend
""",
    parameters={"id": 0},
    result_limit=1000,
)


AGGREGATION = BenchmarkWorkload(
    name="aggregation",
    description="Count all users.",
    query="""
MATCH (u:User)
RETURN count(u)
""",
)


ALL_WORKLOADS = (
    POINT_LOOKUP,
    INDEXED_LOOKUP,
    RELATIONSHIP_LOOKUP,
    TRAVERSAL_1_HOP,
    TRAVERSAL_2_HOP,
    TRAVERSAL_3_HOP,
    AGGREGATION,
)