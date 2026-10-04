from playwright.sync_api import Page, expect
from lib.user_repository import UserRepository
from flask import session

def test_user_not_logged_in_is_redirected_from_booking_requests(web_client):
    response = web_client.get("/booking_requests")
    assert response.status_code == 302
    assert response.location.endswith("/sessions/new")

def test_owner_can_see_booking_requests(page: Page, test_web_address, db_connection):
    db_connection.seed("seeds/clear_users.sql")
    db_connection.seed("seeds/clear_listings.sql")
    db_connection.execute("TRUNCATE TABLE booking_requests RESTART IDENTITY CASCADE;")
    user_repo = UserRepository(db_connection)
    user_repo.create({
        "username": "owner",
        "email": "owner@email.com",
        "password": "password"
    })

    user_repo.create({
        "username": "guest",
        "email": "guest@email.com",
        "password": "password"
    })

    db_connection.seed("seeds/add_to_listings.sql")

    db_connection.execute(
        """
        INSERT INTO booking_requests
        (
            listing_id,
            guest_id,
            date
        )
        VALUES (%s,%s,%s)
        """,
        [
            1,
            2,
            "2026-08-15"
        ]
    )


    page.goto(f"http://{test_web_address}/sessions/new")
    page.get_by_placeholder("email").fill("owner@email.com")
    page.get_by_placeholder("password").fill("password")
    page.get_by_role("button", name="Login").click()


    page.goto(f"http://{test_web_address}/booking_requests")
    expect(page.get_by_text("Listing: Cute Cottage")).to_be_visible()
    expect(page.get_by_text("Guest: guest")).to_be_visible()
    expect(page.get_by_text("Date requested: 2026-08-15")).to_be_visible()

    expect(page.get_by_role("button", name="Accept")).to_be_visible()
    expect(page.get_by_role("button", name="Decline")).to_be_visible()



def test_owner_can_accept_booking_request(page: Page, test_web_address, db_connection):
    db_connection.seed("seeds/clear_users.sql")
    db_connection.seed("seeds/clear_listings.sql")
    db_connection.execute("TRUNCATE TABLE booking_requests RESTART IDENTITY CASCADE;")
    db_connection.execute("TRUNCATE TABLE confirmed_bookings RESTART IDENTITY CASCADE;")

    user_repo = UserRepository(db_connection)
    user_repo.create({
        "username": "owner",
        "email": "owner@email.com",
        "password": "password"
    })

    user_repo.create({
        "username": "guest",
        "email": "guest@email.com",
        "password": "password"
    })


    db_connection.seed("seeds/add_to_listings.sql")


    db_connection.execute(
        """
        INSERT INTO booking_requests
        (
            listing_id,
            guest_id,
            date
        )
        VALUES (%s,%s,%s)
        """,
        [
            1,
            2,
            "2026-08-15"
        ]
    )


    page.goto(f"http://{test_web_address}/sessions/new")
    page.get_by_placeholder("email").fill("owner@email.com")
    page.get_by_placeholder("password").fill("password")
    page.get_by_role("button", name="Login").click()
    page.goto(f"http://{test_web_address}/booking_requests")
    page.get_by_role("button", name="Accept").click()

    assert page.url.endswith("/booking_requests")

    booking_requests = db_connection.execute("SELECT * FROM booking_requests")
    assert len(booking_requests) == 0

    confirmed_bookings = db_connection.execute("SELECT * FROM confirmed_bookings")

    assert len(confirmed_bookings) == 1
    assert confirmed_bookings[0]["listing_id"] == 1
    assert confirmed_bookings[0]["guest_id"] == 2
    assert str(confirmed_bookings[0]["date"]) == "2026-08-15"


def test_owner_can_decline_booking_request(page: Page, test_web_address, db_connection):
    db_connection.seed("seeds/clear_users.sql")
    db_connection.seed("seeds/clear_listings.sql")
    db_connection.execute("TRUNCATE TABLE booking_requests RESTART IDENTITY CASCADE;")
    db_connection.execute("TRUNCATE TABLE confirmed_bookings RESTART IDENTITY CASCADE;")

    user_repo = UserRepository(db_connection)
    user_repo.create({
        "username": "owner",
        "email": "owner@email.com",
        "password": "password"
    })

    user_repo.create({
        "username": "guest",
        "email": "guest@email.com",
        "password": "password"
    })

    db_connection.seed("seeds/add_to_listings.sql")

    db_connection.execute(
        """
        INSERT INTO booking_requests
        (
            listing_id,
            guest_id,
            date
        )
        VALUES (%s,%s,%s)
        """,
        [
            1,
            2,
            "2026-08-15"
        ]
    )


    page.goto(f"http://{test_web_address}/sessions/new")
    page.get_by_placeholder("email").fill("owner@email.com")
    page.get_by_placeholder("password").fill("password")
    page.get_by_role("button", name="Login").click()

    page.goto(f"http://{test_web_address}/booking_requests")
    page.get_by_role("button", name="Decline").click()

    assert page.url.endswith("/booking_requests")
    booking_requests = db_connection.execute("SELECT * FROM booking_requests;")

    assert len(booking_requests) == 0
    confirmed_bookings = db_connection.execute("SELECT * FROM confirmed_bookings")
    assert len(confirmed_bookings) == 0