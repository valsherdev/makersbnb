from lib.user_repository import UserRepository


def test_user_repo_adds_to_database(db_connection, bcrypt):
    db_connection.seed("seeds/clear_users.sql")
    db_connection.seed("seeds/users.sql")

    user_repo = UserRepository(db_connection)
    user_repo.create({"username": "test", "email": "test", "password": "test"})

    new_user = user_repo.find_by_username("test")

    assert new_user.id == 1
    assert new_user.username == "test"
    assert new_user.email == "test"
    assert bcrypt.check_password_hash(new_user.password, "test")


def test_user_repo_find_by_username_works(db_connection, bcrypt):
    db_connection.seed("seeds/clear_users.sql")
    db_connection.seed("seeds/users.sql")

    user_repo = UserRepository(db_connection)
    user_repo.create({"username": "test", "email": "test", "password": "test"})

    new_user = user_repo.find_by_username("test")

    assert new_user.id == 1
    assert new_user.username == "test"
    assert new_user.email == "test"
    assert bcrypt.check_password_hash(new_user.password, "test")


def test_user_repo_find_by_email_works(db_connection, bcrypt):
    db_connection.seed("seeds/clear_users.sql")
    db_connection.seed("seeds/users.sql")

    user_repo = UserRepository(db_connection)
    user_repo.create({"username": "test", "email": "test@test.com", "password": "test"})

    new_user = user_repo.find_by_email("test@test.com")

    assert new_user.id == 1
    assert new_user.username == "test"
    assert new_user.email == "test@test.com"
    assert bcrypt.check_password_hash(new_user.password, "test")


def test_check_password_works(db_connection):
    db_connection.seed("seeds/clear_users.sql")
    db_connection.seed("seeds/users.sql")

    user_repo = UserRepository(db_connection)
    user_repo.create({"username": "test", "email": "test@test.com", "password": "test"})

    new_user = user_repo.find_by_email("test@test.com")

    assert user_repo.check_password_matches(new_user, "test")
