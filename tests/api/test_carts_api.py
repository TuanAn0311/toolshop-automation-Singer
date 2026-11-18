"""Sprint 2 shopping cart API tests."""
import pytest

pytestmark = pytest.mark.api


@pytest.fixture
def new_cart(api):
    """Create a fresh cart and return its id."""
    response = api.post("/carts")
    assert response.status in (200, 201), response.text()
    body = response.json()
    cart_id = body.get("id", body.get("cart_id"))
    assert cart_id is not None, body
    return cart_id


def test_cart_add_product_quantity_two_is_stored(api, new_cart):
    """Goal: verify cart writes and reads through HTTP.
    Precondition: a fresh cart and an available product exist.
    Expected: GET returns the added product with quantity two."""
    products_response = api.get("/products")
    assert products_response.status == 200, products_response.text()
    product_id = products_response.json()["data"][0]["id"]
    added = api.post(f"/carts/{new_cart}", data={"product_id": product_id, "quantity": 2})
    assert added.status in (200, 201), added.text()
    fetched = api.get(f"/carts/{new_cart}")
    assert fetched.status == 200, fetched.text()
    body = fetched.json()
    items = body["cart_items"]
    matching = [item for item in items if str(item.get("product_id")) == str(product_id)]
    assert matching and matching[0]["quantity"] == 2

