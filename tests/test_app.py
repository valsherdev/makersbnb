from playwright.sync_api import Page, expect

# Tests for your routes go here

"""
We can render the index page
"""


def test_get_index(page, test_web_address):
    # We load a virtual browser and navigate to the /index page
    page.goto(f"http://{test_web_address}/")

    # We look at the <p> tag
    heading = page.locator("h1")

    # We assert that it has the text "This is the homepage."
    expect(heading).to_have_text("MakersBnB")
