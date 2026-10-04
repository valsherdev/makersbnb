class Listing:
    def __init__(
        self,
        owner_id,
        name,
        description,
        price_per_night,
        start_date,
        end_date,
        image_path,
        id=None,
    ):
        self.owner_id = owner_id
        self.name = name
        self.description = description
        self.price_per_night = price_per_night
        self.start_date = start_date
        self.end_date = end_date
        self.image_path = image_path
        self.id = id

    def __eq__(self, other):
        return self.__dict__ == other.__dict__
