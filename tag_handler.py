import db

# get tags of a reservation
def get_tags(reservation_id):
    sql = """SELECT tag
             FROM tags
             WHERE reservation_id = ?"""
    return db.query(sql, [reservation_id])

# add a tag into a reservation
def add_tag(tag, reservation_id):
    sql = """INSERT INTO tags
             VALUES (?, ?)"""
    db.execute(sql, [tag, reservation_id])

    tag_id = db.last_insert_id()
    return tag_id

# get all allowed tags
def get_allowed():
    sql = """SELECT tag
             FROM allowed_tags"""
    return db.query(sql)

# check if a tag is allowed
def is_allowed(tag):
    sql = """SELECT tag
             FROM allowed_tags
             WHERE tag = ?"""
    return db.query(sql, [tag])

# add a new allowed tag
def add_allowed(tag):
    sql = """INSERT INTO allowed_tags
             VALUES (?)"""
    db.execute(sql, [tag])
    tag_id = db.last_insert_id()
    return tag_id