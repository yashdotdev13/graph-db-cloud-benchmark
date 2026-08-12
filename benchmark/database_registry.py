from config.settings import load_database_config
from databases.arcadedb import ArcadeDBAdapter
from databases.cognodb import CognoDBAdapter
from databases.falkordb import FalkorDBAdapter
from databases.memgraph import MemgraphAdapter
from databases.neo4j import Neo4jAdapter
from databases.base import GraphDatabaseAdapter


def create_adapter(database: str) -> GraphDatabaseAdapter:
    name = database.upper()

    if name == "NEO4J":
        config = load_database_config(
            "NEO4J",
            database="neo4j",
        )
        return Neo4jAdapter(config)

    if name == "MEMGRAPH":
        config = load_database_config("MEMGRAPH")
        return MemgraphAdapter(config)

    if name == "FALKORDB":
        config = load_database_config("FALKORDB")
        return FalkorDBAdapter(config)

    if name == "ARCADEDB":
        config = load_database_config("ARCADEDB")
        return ArcadeDBAdapter(config)

    if name == "COGNODB":
        config = load_database_config("COGNODB")
        return CognoDBAdapter(config)

    raise ValueError(
        f"Unsupported database: {database}"
    )
