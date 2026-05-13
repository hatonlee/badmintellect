DROP TABLE IF EXISTS comments;
DROP TABLE IF EXISTS tags;
DROP TABLE IF EXISTS allowed_tags;
DROP TABLE IF EXISTS enrollments;
DROP TABLE IF EXISTS reservations;
DROP TABLE IF EXISTS users;

DROP INDEX IF EXISTS idx_reservations_user_id;
DROP INDEX IF EXISTS idx_reservations_title;
DROP INDEX IF EXISTS idx_reservations_place;
DROP INDEX IF EXISTS idx_reservations_date;
DROP INDEX IF EXISTS idx_reservations_time;
DROP INDEX IF EXISTS idx_reservations_duration;

DROP INDEX IF EXISTS idx_tags_reservation_id;
DROP INDEX IF EXISTS idx_tags_tag;

DROP INDEX IF EXISTS idx_comments_reservation_id;
DROP INDEX IF EXISTS idx_comments_user_id;

CREATE TABLE users (
    user_id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    user_role, TEXT,
    password_hash TEXT,
    profile_picture BLOB
);

CREATE TABLE reservations (
    reservation_id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users,
    title TEXT,
    place TEXT,
    date TEXT,
    time TEXT,
    duration TEXT
);

CREATE TABLE tags (
    tag_id INTEGER PRIMARY KEY,
    reservation_id INTEGER REFERENCES reservations,
    tag TEXT
);

CREATE TABLE allowed_tags (
    allowed_tag_id INTEGER PRIMARY KEY,
    tag TEXT UNIQUE
);

CREATE TABLE comments (
    comment_id INTEGER PRIMARY KEY,
    user_id TEXT REFERENCES users,
    reservation_id INTEGER REFERENCES reservations,
    comment TEXT,
    post_time TEXT
);

CREATE TABLE enrollments (
    user_id INTEGER,
    reservation_id INTEGER,
    PRIMARY KEY (user_id, reservation_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (reservation_id) REFERENCES reservations(reservation_id)
);