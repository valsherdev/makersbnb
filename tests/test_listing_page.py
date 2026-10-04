from playwright.sync_api import Page, expect
from lib.user_repository import UserRepository
from flask import session


def test_submitted_booking_request_is_added_to_database(db_connection, test_web_address, page: Page):
    db_connection.seed("seeds/clear_listings.sql")
    db_connection.seed("seeds/clear_users.sql")
    db_connection.execute("TRUNCATE TABLE booking_requests RESTART IDENTITY CASCADE;")
    user_repo = UserRepository(db_connection)
    user_repo.create({
        "username": "test1",
        "email": "test1",
        "password": "test1"
    })
    db_connection.execute(
        """
        INSERT INTO listings 
        (
            owner_id,
            name,
            description,
            price_per_night,
            start_date,
            end_date,
            image_path
        )
        VALUES (%s,%s,%s,%s,%s,%s, %s)
        """,
        [
            1,
            "Cute Cottage in Northumberland",
            "Address: Alwinton National Park, NE65 7BE",
            75,
            "2026-07-16",
            "2026-07-20",
            "dummy.jpg"
        ],
    )


    page.goto(f"http://{test_web_address}/sessions/new")
    page.get_by_placeholder("email").fill("test1")
    page.get_by_placeholder("password").fill("test1")
    page.get_by_role("button", name="Login").click()

    page.goto(f"http://{test_web_address}/listings/1")
    page.locator("#date").fill("2026-07-19")
    page.get_by_text("Submit").click()

    result = db_connection.execute("SELECT * FROM booking_requests")

    assert len(result) == 1
    assert result[0]["listing_id"] == 1
    assert result[0]["guest_id"] == 1
    assert str(result[0]["date"]) == "2026-07-19"



def test_individual_listing_page_returns_200(page: Page, test_web_address, db_connection):
    db_connection.seed("seeds/clear_users.sql")
    db_connection.seed("seeds/clear_listings.sql")
    db_connection.execute(
        """
        INSERT INTO users
        (username, email, password)
        VALUES (%s,%s,%s)
        """,
        [
            "owner",
            "owner@email.com",
            "password"
        ]
    )

    db_connection.execute(
        """
        INSERT INTO listings
        (
            owner_id,
            name,
            description,
            price_per_night,
            start_date,
            end_date,
            image_path
        )
        VALUES (%s,%s,%s,%s,%s,%s, %s)
        """,
        [
            1,
            "Cute Cottage",
            "Lovely cottage",
            75,
            "2026-07-16",
            "2026-07-20",
            "dummy.jpg"
        ]
    )

    response = page.goto(f"http://{test_web_address}/listings/1")
    assert response.status == 200


def test_individual_listing_page_displays_details(page: Page, test_web_address, db_connection):
    db_connection.seed("seeds/clear_users.sql")
    db_connection.seed("seeds/clear_listings.sql")
    db_connection.execute(
        """
        INSERT INTO users
        (username, email, password)
        VALUES (%s,%s,%s)
        """,
        [
            "owner",
            "owner@email.com",
            "password"
        ]
    )

    db_connection.execute(
        """
        INSERT INTO listings
        (
            owner_id,
            name,
            description,
            price_per_night,
            start_date,
            end_date,
            image_path
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s)
        """,
        [
            1,
            "Cute Cottage",
            "Lovely cottage",
            75,
            "2026-07-16",
            "2026-07-20",
            "dummy.jpg"
        ]
    )

    page.goto(f"http://{test_web_address}/listings/1")
    expect(page.get_by_text("Cute Cottage")).to_be_visible()
    expect(page.get_by_text("Lovely cottage")).to_be_visible()
    expect(page.get_by_text("75 GBP per night")).to_be_visible()
    expect(page.get_by_text("2026-07-16")).to_be_visible()
    expect(page.get_by_text("2026-07-20")).to_be_visible()



def test_individual_listing_page_displays_booking_form(page: Page, test_web_address, db_connection):
    db_connection.seed("seeds/clear_users.sql")
    db_connection.seed("seeds/clear_listings.sql")
    db_connection.execute(
        """
        INSERT INTO users
        (username, email, password)
        VALUES (%s,%s,%s)
        """,
        [
            "owner",
            "owner@email.com",
            "password"
        ]
    )

    db_connection.execute(
        """
        INSERT INTO listings
        (
            owner_id,
            name,
            description,
            price_per_night,
            start_date,
            end_date,
            image_path
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s)
        """,
        [
            1,
            "Cute Cottage",
            "Lovely cottage",
            75,
            "2026-07-16",
            "2026-07-20",
            "dummy.jpg"
        ]
    )

    page.goto(f"http://{test_web_address}/listings/1")
    expect(page.locator("form")).to_be_visible()
    expect(page.locator("#date")).to_be_visible()
    expect(page.get_by_text("Submit")).to_be_visible()


def test_user_not_logged_in_is_redirected_to_login(web_client):
    response = web_client.post("/listings/1", data={"date": "2026-07-19"})
    assert response.status_code == 302
    assert response.location.endswith("/sessions/new")


def test_booking_request_fails_if_date_before_availability(web_client, db_connection):
    db_connection.seed("seeds/clear_users.sql")
    db_connection.seed("seeds/clear_listings.sql")
    db_connection.execute(
        """
        INSERT INTO users
        (username,email,password)
        VALUES (%s,%s,%s)
        """,
        [
            "guest",
            "guest@email.com",
            "password"
        ]
    )

    db_connection.execute(
        """
        INSERT INTO listings
        (
            owner_id,
            name,
            description,
            price_per_night,
            start_date,
            end_date,
            image_path
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s)
        """,
        [
            1,
            "House",
            "Nice house",
            100,
            "2026-08-10",
            "2026-08-30",
            "dummy.jpg"
        ]
    )

    with web_client.session_transaction() as session:
        session["user_id"] = 1
    response = web_client.post("/listings/1",
        data={
            "date": "2026-08-05"
        }
    )

    assert response.status_code == 302
    assert response.location.endswith("/booking_request/failed")


def test_booking_request_fails_if_date_already_booked(web_client, db_connection):
    db_connection.seed("seeds/clear_users.sql")
    db_connection.seed("seeds/clear_listings.sql")
    db_connection.execute("TRUNCATE TABLE confirmed_bookings RESTART IDENTITY CASCADE;")
    db_connection.execute("TRUNCATE TABLE booking_requests RESTART IDENTITY CASCADE;")
    db_connection.execute(
        """
        INSERT INTO users
        (username, email, password)
        VALUES
        (%s,%s,%s),
        (%s,%s,%s)
        """,
        [
            "owner",
            "owner@email.com",
            "password",
            "guest",
            "guest@email.com",
            "password"
        ]
    )

    db_connection.execute(
        """
        INSERT INTO listings
        (
            owner_id,
            name,
            description,
            price_per_night,
            start_date,
            end_date,
            image_path
        )
        VALUES
        (%s,%s,%s,%s,%s,%s,%s)
        """,
        [
            1,
            "Cute Cottage",
            "Lovely cottage",
            100,
            "2026-08-10",
            "2026-08-20",
            "dummy.jpg"
        ]
    )

    db_connection.execute(
        """
        INSERT INTO confirmed_bookings
        (
            listing_id,
            guest_id,
            date
        )
        VALUES
        (%s,%s,%s)
        """,
        [
            1,
            2,
            "2026-08-15"
        ]
    )

    with web_client.session_transaction() as session:
        session["user_id"] = 2

    response = web_client.post("/listings/1", data={
            "date": "2026-08-15"
        }
    )


    assert response.status_code == 302
    assert response.location.endswith("/booking_request/failed")
    result = db_connection.execute("SELECT * FROM booking_requests")
    assert len(result) == 0


def test_booking_request_fails_if_date_after_availability(web_client, db_connection):
    db_connection.seed("seeds/clear_users.sql")
    db_connection.seed("seeds/clear_listings.sql")
    db_connection.execute("TRUNCATE TABLE booking_requests RESTART IDENTITY CASCADE;")
    db_connection.execute(
        """
        INSERT INTO users
        (username,email,password)
        VALUES (%s,%s,%s)
        """,
        [
            "guest",
            "guest@email.com",
            "password"
        ]
    )

    db_connection.execute(
        """
        INSERT INTO listings
        (
            owner_id,
            name,
            description,
            price_per_night,
            start_date,
            end_date,
            image_path
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s)
        """,
        [
            1,
            "House",
            "Nice house",
            100,
            "2026-08-10",
            "2026-08-20",
            "dummy.jpg"
        ]
    )

    with web_client.session_transaction() as session:
        session["user_id"] = 1
    
    response = web_client.post("/listings/1", data={
            "date": "2026-08-25"
        }
    )

    assert response.status_code == 302
    assert response.location.endswith("/booking_request/failed")