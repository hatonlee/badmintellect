import db

# get comments of a reservation
def get_comments(reservation_id):
    sql = """SELECT comment
             FROM comments
             WHERE reservation_id = ?"""
    result = db.query(sql, [reservation_id])
    return result if result else None

# add a comment into a reservation
def add_comment(comment, reservation_id):
    sql = """INSERT INTO comments (comment, reservation_id)
             VALUES (?, ?)"""
    db.execute(sql, [comment, reservation_id])

    comment_id = db.last_insert_id()
    return comment_id

# remove a comment from a reservation
def remove_comments(c_id="-1", r_id="-1"):
    sql = """DELETE FROM comments
             WHERE id LIKE ? AND reservation_id LIKE ?"""
    db.execute(sql, [c_id, r_id])