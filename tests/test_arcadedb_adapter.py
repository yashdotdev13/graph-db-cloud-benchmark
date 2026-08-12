from dotenv import load_dotenv

from config.settings import load_database_config
from databases.arcadedb import ArcadeDBAdapter


load_dotenv()


def main() -> None:
    config = load_database_config("ARCADEDB")

    adapter = ArcadeDBAdapter(config)

    try:
        adapter.connect()
        print("1. Health check: PASS")

        result = adapter.execute(
            "SELECT 1 AS value"
        )

        assert result is not None
        print("2. Query execution: PASS")

        adapter.execute(
            "CREATE VERTEX User SET id = 1"
        )
        print("3. Node creation: PASS")

        result = adapter.execute(
            "SELECT FROM User WHERE id = 1"
        )

        assert result is not None
        print("4. Lookup: PASS")

        adapter.clear()
        print("5. Cleanup: PASS")

    finally:
        adapter.close()


if __name__ == "__main__":
    main()