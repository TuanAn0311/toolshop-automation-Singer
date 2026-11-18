"""Network interception and route based Toolshop UI tests."""
import json
import re

import pytest
from playwright.sync_api import expect

from pages.home_page import HomePage, PRODUCT_LIST

EMPTY_PAGE = {
    "current_page": 1,
    "data": [],
    "from": None,
    "last_page": 1,
    "per_page": 9,
    "to": None,
    "total": 0,
}
IMAGE_URL = re.compile(r".*\.(?:png|jpe?g|webp|avif|svg)(?:\?.*)?$", re.IGNORECASE)


@pytest.mark.ui
@pytest.mark.smoke
def test_home_shows_products_when_image_requests_are_blocked(page):
    """Goal: keep the product grid usable without image resources.
    Precondition: image requests are intercepted before page navigation.
    Expected: products stay visible and at least one image request was aborted."""
    blocked = []

    def block_image(route):
        blocked.append(route.request.url)
        route.abort()

    page.route(IMAGE_URL, block_image)
    home = HomePage(page).open()
    expect(home.product_names.first).to_be_visible()
    assert blocked, "No image request was intercepted"


@pytest.mark.ui
@pytest.mark.smoke
def test_home_empty_products_response_shows_empty_state(page):
    """Goal: verify the empty product list state.
    Precondition: the product list endpoint returns an empty JSON page.
    Expected: the no products message appears and no product names are rendered."""
    page.route(PRODUCT_LIST, lambda route: route.fulfill(
        status=200,
        content_type="application/json",
        body=json.dumps(EMPTY_PAGE),
    ))
    home = HomePage(page).open()
    expect(home.no_results).to_have_text("There are no products found.")
    expect(home.product_names).to_have_count(0)
