CREATE TABLE IF NOT EXISTS listings (
    id SERIAL PRIMARY KEY,
    owner_id INT NOT NULL,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    price_per_night INT NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    image_path TEXT NOT NULL,

    CONSTRAINT fk_owner
    FOREIGN KEY (owner_id)
    REFERENCES users(id)
    ON DELETE CASCADE
);

