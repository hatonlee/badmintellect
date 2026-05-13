import db

def get_comments(reservation_id, page=1, page_size=10):
    sql = """SELECT c.comment_id, c.user_id, c.comment, c.post_time, u.username, u.user_role,u.profile_picture IS NOT NULL AS has_profile_picture
               FROM comments AS c
               JOIN users AS u ON c.user_id = u.user_id
              WHERE c.reservation_id = ?
              ORDER BY c.comment_id DESC
              LIMIT ? OFFSET ?"""

    limit = page_size
    offset = page_size * (page - 1)
    result = db.query(sql, (reservation_id, limit, offset))
    return result if result else None

def get_comment(comment_id):
    sql = """SELECT comment_id, user_id, reservation_id, comment, post_time
               FROM comments
              WHERE comment_id = ?"""

    result = db.query(sql, (comment_id,))
    return result[0] if result else None

def comment_count(reservation_id):
    sql = """SELECT COUNT(*)
               FROM comments
              WHERE reservation_id = ?"""

    result = db.query(sql, (reservation_id,))
    return int(result[0][0]) if result else None

def add_comment(reservation_id, user_id, comment):
    sql = """INSERT INTO comments (reservation_id, user_id, comment, post_time)
             VALUES (?, ?, ?, datetime('now'))"""

    db.execute(sql, (reservation_id, user_id, comment))
    comment_id = db.last_insert_id()
    return comment_id

def remove_comments(reservation_id):
    sql = """DELETE FROM comments
              WHERE reservation_id = ?"""

    db.execute(sql, (reservation_id, ))

def remove_comment(comment_id):
    sql = """DELETE FROM comments
              WHERE comment_id = ?"""

    db.execute(sql, (comment_id,))