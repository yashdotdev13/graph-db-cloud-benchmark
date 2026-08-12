import os

from dotenv import load_dotenv
from neo4j import GraphDatabase


load_dotenv()

uri = os.getenv("COGNODB_URI")
username = os.getenv("COGNODB_USERNAME")
password = os.getenv("COGNODB_PASSWORD")

if not uri or not username or not password:
    raise RuntimeError("CognoDB credentials are missing from .env")

driver = GraphDatabase.driver(
    uri,
    auth=(username, password),
)

try:
    driver.verify_connectivity()
    print("1. Connectivity: PASS")

    with driver.session() as session:

        # Clean previous preflight data
        session.run("MATCH (n) DETACH DELETE n")

        # Create nodes
        session.run("""
            CREATE (:User {id: 1, name: 'Alice'})
            CREATE (:User {id: 2, name: 'Bob'})
        """)
        print("2. Node creation: PASS")

        # Create relationship
        session.run("""
            MATCH (a:User {id: 1}), (b:User {id: 2})
            CREATE (a)-[:KNOWS]->(b)
        """)
        print("3. Relationship creation: PASS")

        # Lookup
        record = session.run("""
            MATCH (u:User {id: 1})
            RETURN u.name AS name
        """).single()

        assert record["name"] == "Alice"
        print("4. Lookup: PASS")

        # Traversal
        record = session.run("""
            MATCH (u:User {id: 1})-[:KNOWS]->(friend:User)
            RETURN count(friend) AS count
        """).single()

        assert record["count"] == 1
        print("5. Traversal: PASS")

        # Aggregation
        record = session.run("""
            MATCH (u:User)
            RETURN count(u) AS count
        """).single()

        assert record["count"] == 2
        print("6. Aggregation: PASS")

        # Cleanup
        session.run("MATCH (n) DETACH DELETE n")
        print("7. Cleanup: PASS")

finally:
    driver.close()