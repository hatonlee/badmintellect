CREATE INDEX idx_reservations_user_id ON reservations(user_id);
CREATE INDEX idx_reservations_title ON reservations(title);
CREATE INDEX idx_reservations_place ON reservations(place);
CREATE INDEX idx_reservations_date ON reservations(date);
CREATE INDEX idx_reservations_time ON reservations(time);
CREATE INDEX idx_reservations_duration ON reservations(duration);

CREATE INDEX idx_tags_reservation_id ON tags(reservation_id);
CREATE INDEX idx_tags_tag ON tags(tag);

CREATE INDEX idx_comments_reservation_id ON comments(reservation_id);
CREATE INDEX idx_comments_user_id ON comments(user_id);