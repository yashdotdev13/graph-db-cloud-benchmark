from dotenv import load_dotenv

from config.settings import load_database_config
from databases.cognodb import CognoDBAdapter


load_dotenv()


def main() -> None:
    config = load_database_config("COGNODB")

    adapter = CognoDBAdapter(config)

    try:
        adapter.connect()
        print("1. Health check: PASS")

        # Ensure a clean database before the adapter test.
        adapter.clear()

        result = adapter.execute(
            "RETURN 1 AS value"
        )

        assert result[0]["value"] == 1
        print("2. Query execution: PASS")

        adapter.execute(
            """
            CREATE (:User {
                id: 1,
                name: 'Alice'
            })
            """
        )

        adapter.execute(
            """
            CREATE (:User {
                id: 2,
                name: 'Bob'
            })
            """
        )

        print("3. Node creation: PASS")

        adapter.execute(
            """
            MATCH (a:User {id: 1}),
                  (b:User {id: 2})
            CREATE (a)-[:KNOWS]->(b)
            """
        )

        print("4. Relationship creation: PASS")

        result = adapter.execute(
            """
            MATCH (u:User {id: 1})
            RETURN u.name AS name
            """
        )

        assert result[0]["name"] == "Alice"
        print("5. Lookup: PASS")

        result = adapter.execute(
            """
            MATCH (u:User {id: 1})-[:KNOWS]->(friend:User)
            RETURN count(friend) AS count
            """
        )

        assert result[0]["count"] == 1
        print("6. Traversal: PASS")

        result = adapter.execute(
            """
            MATCH (u:User)
            RETURN count(u) AS count
            """
        )

        assert result[0]["count"] == 2
        print("7. Aggregation: PASS")

        adapter.clear()
        print("8. Cleanup: PASS")

    finally:
        adapter.close()


if __name__ == "__main__":
    main()