from werkzeug.security import check_password_hash, generate_password_hash
import db

def get_users(user_id="%", username="%"):
    sql = """SELECT u.user_id, u.username, u.user_role, u.profile_picture IS NOT NULL AS has_profile_picture, COUNT(r.reservation_id) AS reservation_count
               FROM users AS u
          LEFT JOIN reservations AS r ON u.user_id = r.user_id
              WHERE u.user_id LIKE ? AND u.username LIKE ?
              GROUP BY u.user_id, u.username, u.profile_picture
              ORDER BY u.user_id"""

    result = db.query(sql, (user_id, username))
    return result if result else None

def get_user(user_id):
    sql = """SELECT username, user_role
               FROM users
              WHERE user_id = ?"""

    result = db.query(sql, (user_id,))
    return result[0] if result else None

def create_user(username, password):
    password_hash = generate_password_hash(password)
    sql = """INSERT INTO users (username, user_role, password_hash)
             VALUES (?, NULL, ?)"""

    db.execute(sql, (username, password_hash))
    user_id = db.last_insert_id()
    return user_id

def check_login(username, password):
    sql = """SELECT user_id, password_hash
               FROM users
              WHERE username = ?"""
    result = db.query(sql, (username,))

    if result:
        user_id, password_hash = result[0]
    else:
        return None

    if check_password_hash(password_hash, password):
        return user_id

def get_profile_picture(user_id):
    sql = """SELECT profile_picture
               FROM users
              WHERE user_id = ?"""

    result = db.query(sql, (user_id,))
    return result[0][0] if result else None

def set_profile_picture(user_id, profile_picture):
    sql = """UPDATE users
                SET profile_picture = ?
              WHERE user_id = ?"""

    db.execute(sql, (profile_picture, user_id))

def give_role(user_id, role):
    sql = """UPDATE users
                SET user_role = ?
              WHERE user_id = ?"""

    db.execute(sql, (profile_picture, user_id))