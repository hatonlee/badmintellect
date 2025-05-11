import db

def get_enrolled_users(reservation_id):
    sql = """SELECT u.user_id, u.username
               FROM enrollments AS e
               JOIN users AS u ON e.user_id = u.user_id
              WHERE e.reservation_id = ?"""

    result = db.execute(sql, (reservation_id,))
    return result if result else None

def get_enrolled_reservations(user_id):
    sql = """SELECT reservation_id
               FROM enrollments
              WHERE user_id = ?"""

    result = db.query(sql, (user_id,))
    return result if result else None

def enrolled_users_count(reservation_id):
    sql = """SELECT COUNT(*)
               FROM enrollments
              WHERE reservation_id = ?"""

    result = db.query(sql, (reservation_id,))
    return result[0][0] if result else 0

def enrolled_reservations_count(user_id):
    sql = """SELECT COUNT(*)
               FROM enrollments
              WHERE user_id = ?"""

    result = db.query(sql, (user_id,))
    return result[0][0] if result else 0

def is_enrolled(user_id, reservation_id):
    sql = """SELECT user_id, reservation_id
               FROM enrollments
              WHERE user_id = ? AND reservation_id = ?"""

    result = db.query(sql, (user_id, reservation_id))
    return bool(result)

def enroll_user(user_id, reservation_id):
    if is_enrolled(user_id, reservation_id):
        return
    sql = """INSERT INTO enrollments (user_id, reservation_id)
             VALUES (?, ?)"""

    db.execute(sql, (user_id, reservation_id))

def unenroll_users(user_id, reservation_id):
    sql = """DELETE FROM enrollments
              WHERE user_id LIKE ? and reservation_id LIKE ?"""

    db.execute(sql, (user_id, reservation_id))