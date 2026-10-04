from lib.confirmed_booking import ConfirmedBooking

class ConfirmedBookingRepository:
    def __init__(self, connection):
        self._connection = connection
    

    def get_by_id(self, id):
        row = self._connection.execute("SELECT * from confirmed_bookings WHERE id = %s", [id])[0] 
        
        return ConfirmedBooking(
            row["listing_id"],
            row["guest_id"],
            row["date"],
            row["id"]
        )

    def create(self, confirmed_booking):
        self._connection.execute(
            "INSERT INTO confirmed_bookings (listing_id, guest_id, date) VALUES (%s, %s, %s)",
            [
                confirmed_booking.listing_id,
                confirmed_booking.guest_id,
                confirmed_booking.date
            ]
        )
        return None
    
    def get_by_listing_id_and_date(self, listing_id, date):
            rows = self._connection.execute("SELECT * FROM confirmed_bookings WHERE listing_id = %s AND date = %s",
                                     [listing_id, date])
            if not rows:
                 return None
            return ConfirmedBooking(
                 rows[0]["listing_id"],
                 rows[0]["guest_id"],
                 rows[0]["date"],
                 rows[0]["id"]
            )
    
    def get_by_guest_id(self, guest_id):
        rows = self._connection.execute("SELECT * FROM confirmed_bookings WHERE guest_id = %s",
                                     [guest_id])
        confirmed_bookings = []
        for row in rows:
            item = ConfirmedBooking(
                row["listing_id"],
                row["guest_id"],
                row["date"],
                row["id"]
            )
            confirmed_bookings.append(item)
        return confirmed_bookings 
