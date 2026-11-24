import pytest
from playwright.sync_api import expect
from pytest_bdd import given, parsers, scenarios, then, when

from pages.home_page import HomePage

pytestmark = [pytest.mark.bdd, pytest.mark.ui, pytest.mark.usefixtures("page")]

scenarios("cart.feature")


@given("I am browsing the catalog with an empty cart", target_fixture="home")
def browse_catalog(page):
    return HomePage(page).open()


@when(parsers.parse('I search for "{keyword}" and select "{name}"'), target_fixture="product")
def select_product(home, keyword, name):
    home.search(keyword)
    expect(home.search_completed).to_be_visible()
    expect(home.search_caption).to_contain_text(keyword)
    product = home.open_product(name)
    expect(product.name).to_have_text(name)
    return product


@when(parsers.parse("I add {quantity:d} units to my cart"), target_fixture="cart_details")
def add_product(product, quantity):
    unit_price = product.price()
    product.add_to_cart(quantity)
    expect(product.cart_quantity).to_have_text(str(quantity))
    return product.go_to_cart(), unit_price, quantity


@then(parsers.parse('my cart shows {quantity:d} units of "{name}"'))
def check_cart_product(cart_details, quantity, name):
    cart, _, _ = cart_details
    expect(cart.product_titles).to_have_text([name])
    expect(cart.quantities.first).to_have_value(str(quantity))


@then("the line price is the product's unit price times the quantity")
def check_line_price(cart_details):
    cart, unit_price, quantity = cart_details
    assert cart.line_totals() == [pytest.approx(unit_price * quantity, abs=0.001)]


@then("the cart total is the sum of its line prices")
def check_cart_total(cart_details):
    cart, _, _ = cart_details
    assert cart.total_value() == pytest.approx(sum(cart.line_totals()), abs=0.001)
