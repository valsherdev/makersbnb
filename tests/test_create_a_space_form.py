from playwright.sync_api import Page, expect
from lib.database_connection import get_flask_database_connection
from lib.user_repository import UserRepository
import os

def test_get_route(page: Page, test_web_address):
    assert page.goto(f"http://{test_web_address}/listings").status == 200


def test_listings_page_displays_create_a_listing_form(page: Page, test_web_address):
    page.goto(f"http://{test_web_address}/listings")
    expect(page.locator("form")).to_be_visible()


def test_submitted_listing_is_added_to_database(
    db_connection, test_web_address, page: Page
):
    db_connection.seed("seeds/clear_listings.sql")
    db_connection.seed("seeds/clear_users.sql")

    page.goto(f"http://{test_web_address}/sessions/new")

    user_repo = UserRepository(db_connection)

    # the user needs to be created like this as the password hashing check
    # will fail if its input manually
    user_repo.create({"username": "test1", "email": "test1", "password": "test1"})

    page.goto(f"http://{test_web_address}/sessions/new")

    page.get_by_placeholder("email").fill("test1")
    page.get_by_placeholder("password").fill("test1")
    page.get_by_role("button", name="Login").click()

    page.goto(f"http://{test_web_address}/listings")

    page.get_by_placeholder("Property name").fill("test_property")
    page.get_by_placeholder("Description").fill("test_desc")
    page.get_by_placeholder("Price").fill("100")
    page.locator("#image_upload").set_input_files("static/images/dummy_cabin.jpg")
    page.locator("#start_date").fill("2026-07-16")
    page.locator("#end_date").fill("2026-07-20")
    page.get_by_text("Submit").click()

    print("AFTER SUBMIT URL:", page.url)
    print("PAGE TEXT:")
    print(page.locator("body").inner_text())

    result = db_connection.execute("SELECT * FROM listings")

    assert len(result) == 1
    assert result[0]["name"] == "test_property"
