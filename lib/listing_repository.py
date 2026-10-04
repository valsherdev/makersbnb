from lib.listing import Listing


class ListingRepository:

    def __init__(self, connection):
        self._connection = connection

    # Retrieve all listings
    def all(self):
        rows = self._connection.execute("SELECT * from listings")
        listings = []
        for row in rows:
            item = Listing(
                row["owner_id"],
                row["name"],
                row["description"],
                row["price_per_night"],
                row["start_date"],
                row["end_date"],
                row["image_path"],
                row["id"],
            )
            listings.append(item)
        return listings

    def create(self, listing):
        self._connection.execute(
            "INSERT INTO listings (owner_id, name, description, price_per_night, start_date, end_date, image_path) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            [
                listing.owner_id,
                listing.name,
                listing.description,
                listing.price_per_night,
                listing.start_date,
                listing.end_date,
                listing.image_path,
            ],
        )
        return None

    def find(self, listing_id):
        rows = self._connection.execute(
            "SELECT * from listings WHERE id=%s", [listing_id]
        )
        row = rows[0]
        return Listing(
            row["owner_id"],
            row["name"],
            row["description"],
            row["price_per_night"],
            row["start_date"],
            row["end_date"],
            row["image_path"],
            row["id"],
        )
