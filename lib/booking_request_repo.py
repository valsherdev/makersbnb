from lib.booking_request import BookingRequest

class BookingRequestRepository:
    def __init__(self, connection):
        self._connection = connection
    

    def get_by_owner_id(self, owner_id):
        rows = self._connection.execute(
            "SELECT " \
            "booking_requests.* " \
            "from booking_requests " \
            "JOIN listings " \
            "ON booking_requests.listing_id = listings.id " \
            "WHERE listings.owner_id = %s",
            [owner_id]
        )
        booking_requests = []
        for row in rows:
            item = BookingRequest(
                row["listing_id"],
                row["guest_id"],
                row["date"],
                row["id"]
            )
            booking_requests.append(item)
        return booking_requests
    
    def get_by_id(self, id):
        row = self._connection.execute("SELECT * from booking_requests WHERE id = %s", [id])[0] 
        
        return BookingRequest(
            row["listing_id"],
            row["guest_id"],
            row["date"],
            row["id"]
        )

    def create(self, booking_request):
        self._connection.execute(
            "INSERT INTO booking_requests (listing_id, guest_id, date) VALUES (%s, %s, %s)",
            [
                booking_request.listing_id,
                booking_request.guest_id,
                booking_request.date
            ]
        )
        return None
    
    def delete(self, id):
        self._connection.execute("DELETE from booking_requests WHERE id = %s", [id])
        return None
