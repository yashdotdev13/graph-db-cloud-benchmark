from dotenv import load_dotenv

from config.settings import load_database_config
from databases.falkordb import FalkorDBAdapter


load_dotenv()


def main() -> None:
    config = load_database_config("FALKORDB")

    adapter = FalkorDBAdapter(config)

    try:
        adapter.connect()

        assert adapter.health_check()
        print("1. Health check: PASS")

        result = adapter.execute(
            "RETURN 1"
        )

        assert result is not None
        print("2. Query execution: PASS")

        adapter.execute(
            """
            CREATE (:BenchmarkUser {id: 1})
            """
        )
        print("3. Node creation: PASS")

        result = adapter.execute(
            """
            MATCH (u:BenchmarkUser {id: 1})
            RETURN u.id
            """
        )

        assert result is not None
        print("4. Lookup: PASS")

        adapter.clear()
        print("5. Cleanup: PASS")

    finally:
        adapter.close()


if __name__ == "__main__":
    main()