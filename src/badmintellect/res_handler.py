import db

def get_reservations(page=1, page_size=25, params=None, **kwargs):
    combined = {}
    if params:
        params = {k: v for k, v in params.items() if v not in (None, "")}
        combined.update(params)
    if kwargs:
        kwargs = {k: v for k, v in kwargs.items() if v not in (None, "")}
        combined.update(kwargs)

    # only include times if both values are present
    if combined:
        if "date_start" not in combined or "date_end" not in combined:
            combined.pop("date_start", None)
            combined.pop("date_end", None)
        if "time_start" not in combined or "time_end" not in combined:
            combined.pop("time_start", None)
            combined.pop("time_end", None)
        if "duration_start" not in combined or "duration_end" not in combined:
            combined.pop("duration_start", None)
            combined.pop("duration_end", None)

    sql = f"""SELECT r.reservation_id, r.user_id, r.title, r.place, r.date, r.time, r.duration, u.username, COALESCE(ec.enrolled_count, 0) AS enrolled_count
                FROM reservations AS r
                JOIN users AS u ON r.user_id = u.user_id
           LEFT JOIN (SELECT reservation_id, COUNT(*) AS enrolled_count
                     FROM enrollments
                     GROUP BY reservation_id) AS ec ON r.reservation_id = ec.reservation_id
               WHERE {"r.reservation_id   LIKE ?          AND" if "reservation_id" in combined else ""}
                     {"r.place            LIKE ?          AND" if "place" in combined else ""}
                     {"r.user_id          LIKE ?          AND" if "user_id" in combined else ""}
                     {"r.title            LIKE ?          AND" if "title" in combined else ""}
                     {"r.date             BETWEEN ? AND ? AND" if "date_start" in combined and "date_end" in combined else ""}
                     {"r.time             BETWEEN ? AND ? AND" if "time_start" in combined and "time_end" in combined else ""}
                     {"r.duration         BETWEEN ? AND ? AND" if "duration_start" in combined and "duration_end" in combined else ""}
                     1 = 1
            ORDER BY r.reservation_id DESC
               LIMIT ? OFFSET ?"""

    combined = tuple(combined.values())

    limit = page_size
    offset = page_size * (page - 1)
    combined = (*combined, limit, offset)

    result = db.query(sql, combined)
    return result if result else None

def reservation_count(params=None, **kwargs):
    combined = {}
    if params:
        params = {k: v for k, v in params.items() if v not in (None, "")}
        combined.update(params)
    if kwargs:
        kwargs = {k: v for k, v in kwargs.items() if v not in (None, "")}
        combined.update(kwargs)

    # only include times if both values are present
    if combined:
        if "date_start" not in combined or "date_end" not in combined:
            combined.pop("date_start", None)
            combined.pop("date_end", None)
        if "time_start" not in combined or "time_end" not in combined:
            combined.pop("time_start", None)
            combined.pop("time_end", None)
        if "duration_start" not in combined or "duration_end" not in combined:
            combined.pop("duration_start", None)
            combined.pop("duration_end", None)

    sql = f"""SELECT COUNT(*)
                FROM reservations
               WHERE {"reservation_id   LIKE ?          AND" if "reservation_id" in combined else ""}
                     {"user_id          LIKE ?          AND" if "user_id" in combined else ""}
                     {"place            LIKE ?          AND" if "place" in combined else ""}
                     {"title            LIKE ?          AND" if "title" in combined else ""}
                     {"date             BETWEEN ? AND ? AND" if "date_start" in combined and "date_end" in combined else ""}
                     {"time             BETWEEN ? AND ? AND" if "time_start" in combined and "time_end" in combined else ""}
                     {"duration         BETWEEN ? AND ? AND" if "duration_start" in combined and "duration_end" in combined else ""}
                     1 = 1"""

    combined = tuple(combined.values())
    result = db.query(sql, combined)
    return int(result[0][0]) if result else None

def get_reservation(reservation_id):
    sql = """SELECT r.reservation_id, r.user_id, r.title, r.place, r.date, r.time, r.duration, u.username
               FROM reservations AS r
               JOIN users AS u on r.user_id = u.user_id
              WHERE reservation_id = ?"""

    result = db.query(sql, (reservation_id,))
    return result[0] if result else None

def add_reservation(params=None, **kwargs):
    combined = {}
    if params:
        combined.update(params)
    if kwargs:
        combined.update(kwargs)
    combined = tuple(combined.values())

    sql = """INSERT INTO reservations (user_id, title, place, date, time, duration)
             VALUES (?, ?, ?, ?, ?, ?)"""

    db.execute(sql, combined)
    reservation_id = db.last_insert_id()
    return reservation_id

def update_reservation(params=None, **kwargs):
    combined = {}
    if params:
        combined.update(params)
    if kwargs:
        combined.update(kwargs)
    combined = tuple(combined.values())

    sql = """UPDATE reservations
                SET title = ?, place = ?, date = ?, time = ?, duration = ?
              WHERE reservation_id = ?"""

    db.execute(sql, combined)

def remove_reservation(reservation_id):
    sql = """DELETE FROM reservations
              WHERE reservation_id = ?"""

    db.execute(sql, (reservation_id,))