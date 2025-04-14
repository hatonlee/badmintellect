import db

# get comments of a reservation
def get_comments(reservation_id):
    sql = """SELECT comment
             FROM comments
             WHERE reservation_id = ?"""
    return db.query(sql, [reservation_id])

# add a comment into a reservation
def add_comment(comment, reservation_id):
    sql = """INSERT INTO comments (comment, reservation_id)
             VALUES (?, ?)"""
    db.execute(sql, [comment, reservation_id])

    comment_id = db.last_insert_id()
    return comment_id

# remove a comment from a reservation
def remove_comment(comment_id, reservation_id):
    sql = """DELETE FROM comments
             WHERE id = ? AND reservation_id = ?"""
    db.execute(sql, [comment_id, reservation_id])