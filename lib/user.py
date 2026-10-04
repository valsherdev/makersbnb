class User:
    def __init__(self, username, email, password, id=None):
        self.username = username
        self.email = email
        self.password = password
        self.id = id

    
    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    