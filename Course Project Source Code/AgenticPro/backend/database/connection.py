import sqlite3
from pathlib import Path

from backend.config.settings import settings


def get_connection() -> sqlite3.Connection:
    """Create and return a connection to the SQLite database."""

    path = Path(settings.database_path)

    # Ensure the database directory exists.
    path.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row

    return connection