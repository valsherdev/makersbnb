from playwright.sync_api import Page, expect
from app import app


def test_returns_200_response(page: Page, test_web_address):
    assert page.goto(f"http://{test_web_address}/").status == 200


def test_page_shows_one_listing(page, db_connection, test_web_address):
    db_connection.execute("TRUNCATE TABLE users RESTART IDENTITY CASCADE;")
    db_connection.execute("DROP TABLE listings CASCADE;")
    db_connection.seed("seeds/listings.sql")

    db_connection.seed("seeds/add_to_users.sql")
    db_connection.execute(
        "INSERT INTO listings (owner_id, name, description, price_per_night, start_date, end_date, image_path) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s);",
        [
            1,
            "Cute Cottage in Northumberland",
            "Address: Alwinton National Park, NE65 7BE",
            75,
            "2026/07/16",
            "2026/07/20",
            "dummy_image.jpg"
        ],
    )

    page.goto(f"http://{test_web_address}/")
    listing = page.locator(".listing").first
    # print(listing.inner_text())
    assert "Cute Cottage in Northumberland" in listing.inner_text()
    assert "Address: Alwinton National Park, NE65 7BE" in listing.inner_text()
    assert "75 GBP per night" in listing.inner_text()


def test_page_shows_several_listing(page, db_connection, test_web_address):
    db_connection.seed("seeds/clear_users.sql")
    db_connection.seed("seeds/clear_listings.sql")

    db_connection.seed("seeds/add_to_users.sql")
    db_connection.seed("seeds/add_to_listings.sql")

    page.goto(f"http://{test_web_address}/")
    assert page.locator(".listing").count() == 2
