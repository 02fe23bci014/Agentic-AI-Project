import sqlite3

db_path = "backend/database/evaluations.db"

connection = sqlite3.connect(db_path)

tables = connection.execute(
    "SELECT name FROM sqlite_master WHERE type='table'"
).fetchall()

print("Database tables:", tables)

connection.close()