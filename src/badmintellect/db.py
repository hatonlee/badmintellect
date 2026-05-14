import sqlite3
from collections.abc import Sequence
from typing import Any

from flask import g


def get_connection() -> sqlite3.Connection:
    with sqlite3.connect("database.db") as con:
        con.execute("PRAGMA foreign_keys = ON")
        con.row_factory = sqlite3.Row
    return con


def execute(sql: str, params: Sequence[Any] | None = None) -> None:
    if params is None:
        params = ()

    con = get_connection()
    result = con.execute(sql, params)
    con.commit()
    g.last_insert_id = result.lastrowid
    con.close()


def last_insert_id() -> int:
    return g.last_insert_id


def query(sql: str, params: Sequence[Any] | None = None) -> list[sqlite3.Row]:
    if params is None:
        params = ()

    con = get_connection()
    result = con.execute(sql, params).fetchall()
    con.close()
    return result
