"""Buoi 2 - API testing with APIRequestContext (not the requests library).

Fixtures you can use (see conftest.py): api, test_user, auth_token, auth_headers
Helpers: register_user(api, email, password), new_email(), strong_password()

Run:  pytest tests/buoi2/test_b2_api.py -v
"""
import json
from pathlib import Path

import pytest

from conftest import new_email, register_user, strong_password  # noqa: F401  (you will need them)

KEYWORDS = json.loads((Path(__file__).parents[2] / "data" / "search_keywords.json").read_text(encoding="utf-8"))
pytestmark = pytest.mark.api


# ---------------------------------------------------------------- B2.1 (together)
@pytest.mark.smoke
@pytest.mark.api
def test_status_returns_toolshop(api):
    """Goal: API is alive. Precondition: none. Expected: 200 and app_name Toolshop."""
    response = api.get("/status")
    assert response.status == 200, response.text()
    assert response.json()["app_name"] == "Toolshop"


# ---------------------------------------------------------------- B2.2
def test_b2_2_products_first_page_has_pagination_and_product_shape(api):
    """Goal: contract of GET /products.
    Precondition: none.
    Expected: keys current_page/data/per_page/total/last_page, 0 < len(data) <= per_page,
    every product has id (str or int), a non-empty name and a price > 0.
    Rule: NO absolute numbers (PROD has 50 products, BUGGY 26)."""
    response = api.get("/products")
    assert response.status == 200, response.text()
    body = response.json()
    required = {"current_page", "data", "per_page", "total", "last_page"}
    assert required <= body.keys()
    assert 0 < len(body["data"]) <= body["per_page"]
    assert all(isinstance(item.get("id"), (str, int)) for item in body["data"])
    assert all(item.get("name") and float(item.get("price", 0)) > 0 for item in body["data"])


# ---------------------------------------------------------------- B2.3 data-driven
@pytest.mark.parametrize("case", KEYWORDS, ids=[c["keyword"] for c in KEYWORDS])
def test_b2_3_search_api_returns_only_matching_names(api, case):
    """Goal: GET /products/search?q=... filters by name.
    Precondition: none.
    Expected: at least one result and every name contains the keyword.
    Extra: add "saw" and "wrench" to data/search_keywords.json - no code change needed."""
    response = api.get("/products/search", params={"q": case["keyword"]})
    assert response.status == 200, response.text()
    body = response.json()
    products = body if isinstance(body, list) else body.get("data", [])
    assert products, f"No results for keyword {case['keyword']}"
    assert all(case["keyword"].lower() in item["name"].lower() for item in products)


# ---------------------------------------------------------------- B2.4 errors
@pytest.mark.parametrize(
    ("path", "expected_status"),
    [("/users/me", 401), ("/products/does-not-exist", 404)],
)
def test_b2_4a_protected_or_missing_resource_returns_4xx(api, path, expected_status):
    response = api.get(path)
    assert response.status == expected_status, response.text()


def test_b2_4b_register_empty_body_returns_422_with_field_errors(api):
    """Goal: server-side validation. Precondition: none.
    Expected: 422 and error lists for 'email' and 'password'."""
    response = api.post("/users/register", data={})
    assert response.status == 422, response.text()
    errors = response.json()
    assert "email" in errors and "password" in errors, errors


def test_b2_4c_register_leaked_password_is_rejected(api):
    """Goal: password policy. Precondition: none.
    Expected: 422 because 'Welcome01!' appears in known data leaks."""
    response = register_user(api, new_email(), "Welcome01!")
    assert response.status == 422, response.text()


# ---------------------------------------------------------------- B2.5 token
def test_b2_5a_users_me_with_token_returns_own_profile(api, auth_headers, test_user):
    """Goal: bearer token grants access. Precondition: user registered by the fixture.
    Expected: 200 and the same email."""
    response = api.get("/users/me", headers=auth_headers)
    assert response.status == 200, response.text()
    assert response.json()["email"] == test_user["email"]


def test_b2_5b_register_response_does_not_expose_password(api):
    """Goal: no secrets in responses. Precondition: none.
    Expected: 201 and no 'password' key in the JSON body."""
    response = register_user(api, new_email(), strong_password())
    assert response.status == 201, response.text()
    assert "password" not in response.json()


# ---------------------------------------------------------------- B2.6 your own fixture
@pytest.fixture
def new_cart(api):
    """Create a cart for one API test and return its identifier."""
    response = api.post("/carts")
    assert response.status in (200, 201), response.text()
    body = response.json()
    cart_id = body.get("id", body.get("cart_id"))
    assert cart_id is not None, body
    return cart_id


def test_b2_6_cart_add_product_quantity_two_is_stored(api, new_cart):
    """Goal: cart API stores the quantity.
    Precondition: a new cart (your fixture) and the first product of GET /products.
    Expected: GET /carts/{id} has exactly 1 item, quantity 2, same product_id."""
    products_response = api.get("/products")
    assert products_response.status == 200, products_response.text()
    product_id = products_response.json()["data"][0]["id"]
    added = api.post(f"/carts/{new_cart}", data={"product_id": product_id, "quantity": 2})
    assert added.status in (200, 201), added.text()
    response = api.get(f"/carts/{new_cart}")
    assert response.status == 200, response.text()
    body = response.json()
    items = body["cart_items"]
    assert len(items) == 1, body
    assert str(items[0].get("product_id")) == str(product_id)
    assert items[0].get("quantity") == 2

