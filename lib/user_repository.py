from .user import User
from psycopg import errors
from flask_bcrypt import generate_password_hash, check_password_hash


class UserRepository:

    def __init__(self, connection):
        self._connection = connection

    def create(self, user):
        try:
            new_user = User(**user)
            new_user_details = [
                new_user.username,
                new_user.email,
                generate_password_hash(new_user.password).decode("utf-8"),
            ]
            # print(generate_password_hash(new_user_details[2]))

            if "" in new_user_details:
                print(f"Fields cannot be empty")
                return False
            self._connection.execute(
                "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
                new_user_details,
            )
        except errors.UniqueViolation:
            print(f"Username or email already exists, try again")
            return False
        except errors.InFailedSqlTransaction:
            print(f"Username or email already exists, try again")
            return False
        return None

    def find_by_username(self, username):
        user_details = self._connection.execute(
            "SELECT * FROM users WHERE username = %s", [username]
        )[0]
        return User(
            user_details["username"],
            user_details["email"],
            user_details["password"],
            user_details["id"]
        )
    
    def find_by_id(self, id):
        user_details = self._connection.execute(
            "SELECT * FROM users WHERE id = %s", [id]
        )[0]
        return User(
            user_details["username"],
            user_details["email"],
            user_details["password"],
            user_details["id"]
        )

    def find_by_email(self, email):
        try:
            user_details = self._connection.execute(
                "SELECT * FROM users WHERE email = %s", [email]
            )[
                0
            ]  # get the first item (there should be only one item)
        except IndexError:
            print(f"-- login failed --")
            return None
        return User(
            user_details["username"],
            user_details["email"],
            user_details["password"],
            user_details["id"]
        )

    def check_password_matches(self, user, password):
        return check_password_hash(user.password, password)
