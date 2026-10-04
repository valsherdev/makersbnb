from playwright.sync_api import Page, expect
from lib.user_repository import UserRepository


def test_login_page_loads(page: Page, test_web_address):
    page.goto(f"http://{test_web_address}/sessions/new")

    expect(page.locator("h2")).to_have_text("Login Form")


def test_correct_login_redirects_to_index(page: Page, test_web_address, db_connection):
    db_connection.seed("seeds/clear_users.sql")

    user_repo = UserRepository(db_connection)

    # the user needs to be created like this as the password hashing check
    # will fail if its input manually
    user_repo.create({"username": "test1", "email": "test1", "password": "test1"})

    page.goto(f"http://{test_web_address}/sessions/new")
    # print(page.locator("h2").text_content())

    page.get_by_placeholder("email").fill("test1")
    page.get_by_placeholder("password").fill("test1")
    page.get_by_role("button", name="Login").click()

    # print(dir(page.locator("h1")))
    # print(page.locator("h1").text_content())
    expect(page.locator("h1")).to_have_text("MakersBnB")
