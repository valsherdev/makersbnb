CREATE TABLE IF NOT EXISTS confirmed_bookings (
    id SERIAL PRIMARY KEY,
    listing_id INT NOT NULL,
    guest_id INT NOT NULL,
    date DATE NOT NULL,

    CONSTRAINT fk_guest
    FOREIGN KEY (guest_id)
    REFERENCES users(id)
    ON DELETE CASCADE,

    CONSTRAINT fk_listing
    FOREIGN KEY (listing_id)
    REFERENCES listings(id)
    ON DELETE CASCADE

);