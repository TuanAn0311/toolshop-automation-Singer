"""Sprint 2 API product contract and data driven search tests."""
import json
from pathlib import Path

import pytest

KEYWORDS = json.loads((Path(__file__).parents[2] / "data" / "search_keywords.json").read_text(encoding="utf-8-sig"))
pytestmark = pytest.mark.api


def test_products_response_has_pagination_and_valid_product_shape(api):
    """Goal: verify the products response contract.
    Precondition: the API is available.
    Expected: pagination fields and valid product objects are returned."""
    response = api.get("/products")
    assert response.status == 200, response.text()
    body = response.json()
    assert {"current_page", "data", "per_page", "total", "last_page"} <= body.keys()
    assert 0 < len(body["data"]) <= body["per_page"]
    assert all(isinstance(p.get("id"), (str, int)) for p in body["data"])
    assert all(p.get("name") and float(p.get("price", 0)) > 0 for p in body["data"])


@pytest.mark.parametrize("case", KEYWORDS, ids=[case["keyword"] for case in KEYWORDS])
def test_product_search_returns_only_matching_names(api, case):
    """Goal: search products by data driven keywords.
    Precondition: keyword cases are stored in the JSON data file.
    Expected: matching results contain the requested keyword in every name."""
    response = api.get("/products/search", params={"q": case["keyword"]})
    assert response.status == 200, response.text()
    body = response.json()
    products = body if isinstance(body, list) else body.get("data", [])
    assert products, f"No products found for {case['keyword']}"
    assert all(case["keyword"].lower() in p["name"].lower() for p in products)
