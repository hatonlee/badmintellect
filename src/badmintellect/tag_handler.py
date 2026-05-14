import sqlite3

from . import db


def get_tags(reservation_id: int) -> list[sqlite3.Row]:
    sql = """SELECT tag
               FROM tags
              WHERE reservation_id = ?"""

    return db.query(sql, (reservation_id,))


def get_tag(tag_id: int) -> sqlite3.Row | None:
    sql = """SELECT tag
               FROM tags
              WHERE tag_id = ?"""

    result = db.query(sql, (tag_id,))
    return result[0] if result else None


def add_tag(reservation_id: int, tag: str) -> int:
    sql = """INSERT INTO tags (reservation_id, tag)
             VALUES (?, ?)"""

    db.execute(sql, (reservation_id, tag))
    tag_id = db.last_insert_id()
    return tag_id


def remove_tags(reservation_id: int, tag: str) -> None:
    sql = """DELETE FROM tags
              WHERE reservation_id LIKE ? AND tag LIKE ?"""

    db.execute(sql, (reservation_id, tag))


def get_allowed_tags() -> list[sqlite3.Row] | None:
    sql = """SELECT tag
               FROM allowed_tags"""

    result = db.query(sql)
    return result if result else None


def is_allowed(tag: str) -> bool:
    sql = """SELECT tag
               FROM allowed_tags
              WHERE tag = ?"""

    return bool(db.query(sql, (tag,)))


def add_allowed_tag(tag: str) -> int:
    sql = """INSERT INTO allowed_tags (tag)
             VALUES (?)"""

    db.execute(sql, (tag,))
    tag_id = db.last_insert_id()
    return tag_id
