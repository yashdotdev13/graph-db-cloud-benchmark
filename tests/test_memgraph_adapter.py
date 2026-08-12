from dotenv import load_dotenv

from config.settings import load_database_config
from databases.memgraph import MemgraphAdapter


load_dotenv()


def main() -> None:
    config = load_database_config("MEMGRAPH")

    adapter = MemgraphAdapter(config)

    try:
        adapter.connect()

        assert adapter.health_check()
        print("1. Health check: PASS")

        result = adapter.execute("RETURN 1 AS value")

        assert result[0]["value"] == 1
        print("2. Query execution: PASS")

        adapter.execute(
            "CREATE (:BenchmarkUser {id: $id})",
            {"id": 1},
        )
        print("3. Node creation: PASS")

        result = adapter.execute(
            """
            MATCH (u:BenchmarkUser {id: $id})
            RETURN u.id AS id
            """,
            {"id": 1},
        )

        assert result[0]["id"] == 1
        print("4. Lookup: PASS")

        adapter.clear()

        result = adapter.execute(
            """
            MATCH (u:BenchmarkUser)
            RETURN count(u) AS count
            """
        )

        assert result[0]["count"] == 0
        print("5. Cleanup: PASS")

    finally:
        adapter.close()


if __name__ == "__main__":
    main()