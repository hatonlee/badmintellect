CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    password_hash TEXT
);

CREATE TABLE reservations (
    id INTEGER PRIMARY KEY,
    title TEXT,
    start_time TEXT,
    end_time TEXT,
    place TEXT,
    user_id INTEGER REFERENCES users
);

CREATE TABLE tags (
    id INTEGER PRIMARY KEY,
    tag TEXT,
    reservation_id INTEGER REFERENCES reservations
);

CREATE TABLE allowed_tags (
    id INTEGER PRIMARY KEY,
    tag TEXT UNIQUE
);

CREATE TABLE comments (
    id INTEGER PRIMARY KEY,
    comment TEXT,
    reservation_id INTEGER REFERENCES reservations
)