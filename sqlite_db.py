"""
sqlite_db.py implements sqlite3 to allow for simplistic one-line fashion
"""

import sqlite3
from pathlib import Path


def get_connection(db_path: Path | str) -> sqlite3.Connection:
    """Create and return a database connection."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # Allows dict-like row access
    return conn


def init_db(db_path:Path|str, name:str="data", primary:dict[str,str]=None, columns:dict[str,str]=None) -> None:
    """
    Initialize the SQLite database and create a table if it doesn't exist.
    Dynamically adds any new columns that don't yet exist in the table.

    Args:
        db_path: Path to the SQLite database file.
        :param name: Table name.
        :param primary: Primary table column (Must be length 1)
        :param columns: Dict of column_name -> SQL type, e.g. {"url": "TEXT", "count": "INTEGER"}.
    """

    if primary is None:
        primary = {"id": "INTEGER"}

    conn = get_connection(db_path)
    cur = conn.cursor()

    (primary_col, primary_type) = primary

    # Create table with just the primary key if it doesn't exist
    cur.execute(f"CREATE TABLE IF NOT EXISTS {name} ({primary_col} {primary_type} PRIMARY KEY)")

    # Add any new columns that don't already exist
    if columns:
        cur.execute(f"PRAGMA table_info({name})")
        existing = {row["name"] for row in cur.fetchall()}

        for col_name, col_type in columns.items():
            if col_name not in existing:
                cur.execute(f"ALTER TABLE {name} ADD COLUMN {col_name} {col_type}")

    conn.commit()
    conn.close()


def insert_row(db_path:Path|str, name:str="data", data:dict=None) -> int|None:
    """
    Insert a single row into the table.

    Args:
        db_path: Path to the SQLite database file.
        name: Table name.
        data: Dict of column_name -> value, e.g. {"url": "https://...", "count": 3}.

    Returns:
        The row ID of the inserted record, or None if no data provided.
    """
    if not data:
        return None

    conn = get_connection(db_path)
    cur = conn.cursor()

    columns = ", ".join(data.keys())
    placeholders = ", ".join("?" * len(data))

    cur.execute(
        f"INSERT INTO {name} ({columns}) VALUES ({placeholders})",
        tuple(data.values())
    )

    row_id = cur.lastrowid
    conn.commit()
    conn.close()
    return row_id


def insert_rows(db_path:Path|str, name:str="data", rows:list[dict]=None) -> int:
    """
    Insert multiple rows into the table efficiently.

    Args:
        db_path: Path to the SQLite database file.
        name: Table name.
        rows: List of dicts, each representing a row.

    Returns:
        Number of rows inserted.
    """
    if not rows:
        return 0

    conn = get_connection(db_path)
    cur = conn.cursor()

    columns = ", ".join(rows[0].keys())
    placeholders = ", ".join("?" * len(rows[0]))

    cur.executemany(
        f"INSERT INTO {name} ({columns}) VALUES ({placeholders})",
        [tuple(row.values()) for row in rows]
    )

    count = cur.rowcount
    conn.commit()
    conn.close()
    return count


def fetch_all(db_path: Path | str, name: str = "data") -> list[dict]:
    """Fetch all rows from a table as a list of dicts."""
    conn = get_connection(db_path)
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM {name}")
    rows = [dict(row) for row in cur.fetchall()]
    conn.close()
    return rows

if __name__ == "__main__":
    DB = "mydata.db"

    # 1. Initialise (create table + declare columns)
    init_db(DB, name="urls", columns={
        "url":   "TEXT NOT NULL",
        "mode":  "TEXT",
        "count": "INTEGER DEFAULT 0",
    })

    # 2. Insert a single row
    new_row = insert_row(DB, name="urls", data={
        "url":   "https://example.com",
        "mode":  "GET",
        "count": 1,
    })
    print(f"Inserted row: {new_row}")

    # 3. Insert multiple rows at once
    insert_rows(DB, name="urls", rows=[
        {"url": "https://foo.com", "mode": "POST", "count": 2},
        {"url": "https://bar.com", "mode": "GET",  "count": 0},
    ])

    # 4. Read it back
    for row in fetch_all(DB, name="urls"):
        print(row)