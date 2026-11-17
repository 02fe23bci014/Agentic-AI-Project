from backend.database.connection import get_connection

connection = get_connection()

try:
    tables = connection.execute(
        "SELECT name FROM sqlite_master "
        "WHERE type = 'table' AND name NOT LIKE 'sqlite_%' "
        "ORDER BY name"
    ).fetchall()

    for table in tables:
        table_name = table["name"]

        print(f"\n{'=' * 40}")
        print(f"TABLE: {table_name}")
        print("=" * 40)

        columns = connection.execute(
            f'PRAGMA table_info("{table_name}")'
        ).fetchall()

        for column in columns:
            print(
                f"Column: {column['name']} | "
                f"Type: {column['type']} | "
                f"Primary key: {bool(column['pk'])}"
            )

        count = connection.execute(
            f'SELECT COUNT(*) FROM "{table_name}"'
        ).fetchone()[0]

        print(f"Number of records: {count}")

finally:
    connection.close()