import db

# get a list of all the matching reservations and their details
def get_reservations(r_id="%", r_title="%", r_start_time="%", r_end_time="%", r_place="%"):
    sql = """SELECT *
             FROM reservations
             WHERE id LIKE ? AND title LIKE ? AND start_time LIKE ? AND end_time LIKE ? AND place LIKE ?
             ORDER BY id DESC"""
    return db.query(sql, [r_id, r_title, r_start_time, r_end_time, r_place])

# get the details of a reservation
def get_reservation(reservation_id):
    sql = "SELECT * FROM reservations WHERE id = ?"
    return db.query(sql, [reservation_id])[0]

# add a new reservation into the database
def add_reservation(title, start_time, end_time, place, user_id):
    sql = "INSERT INTO reservations (title, start_time, end_time, place, user_id) VALUES (?, ?, ?, ?, ?)"
    db.execute(sql, [title, start_time, end_time, place, user_id])
    reservation_id = db.last_insert_id()
    return reservation_id

# update a reservation with new values
def update_reservation(reservation_id, new_title, new_start_time, new_end_time, new_place):
    sql = "UPDATE reservations SET title = ?, start_time = ?, end_time = ?, place = ? WHERE id = ?"
    db.execute(sql, [new_title, new_start_time, new_end_time, new_place, reservation_id])

# remove a reservation with a specified id
def remove_reservation(reservation_id):
    sql = "DELETE FROM reservations WHERE id = ?"
    db.execute(sql, [reservation_id])