from benchmark.workload import BenchmarkWorkload


POINT_LOOKUP = BenchmarkWorkload(
    name="point_lookup",
    description="Lookup a single user by ID.",
    query="""
        MATCH (u:User {id: $id})
        RETURN u
    """,
)


RELATIONSHIP_LOOKUP = BenchmarkWorkload(
    name="relationship_lookup",
    description="Find direct relationships for a user.",
    query="""
        MATCH (u:User {id: $id})-[:KNOWS]->(friend)
        RETURN friend
    """,
)


TRAVERSAL = BenchmarkWorkload(
    name="traversal",
    description="Traverse a multi-hop relationship path.",
    query="""
        MATCH (u:User {id: $id})-[:KNOWS*1..3]->(friend)
        RETURN friend
    """,
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
    RELATIONSHIP_LOOKUP,
    TRAVERSAL,
    AGGREGATION,
)