class ConfirmedBooking:
    def __init__(self, listing_id, guest_id, date, id=None):
        self.listing_id = listing_id
        self.guest_id = guest_id
        self.date = date
        self.id = id

    def __eq__(self, other):
        return self.__dict__ == other.__dict__