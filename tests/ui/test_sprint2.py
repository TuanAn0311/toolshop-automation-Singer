"""Additional Toolshop UI coverage for Sprint 2."""
import re

import pytest
from playwright.sync_api import expect

from pages.account_page import AccountPage
from pages.home_page import HomePage
from pages.login_page import LoginPage


@pytest.mark.ui
@pytest.mark.parametrize("order", ["price,asc", "price,desc"])
def test_product_list_sorts_by_price(page, order):
    """Goal: sort the product list by price.
    Precondition: the home product list is loaded.
    Expected: displayed prices follow the selected order."""
    home = HomePage(page).open()
    expect(home.product_names.first).to_be_visible()
    home.sort_by(order)
    expect(home.sorting_completed).to_be_visible()
    prices = home.prices()
    assert prices == sorted(prices, reverse=order.endswith("desc")), prices


@pytest.mark.ui
def test_hammer_category_shows_only_hammer_products(page):
    """Goal: filter products by the Hammer category.
    Precondition: the home product list is loaded.
    Expected: every visible product name contains hammer."""
    home = HomePage(page).open().filter_hammer_category()
    expect(home.product_names.first).to_be_visible()
    names = home.product_names.all_inner_texts()
    assert names and all("hammer" in name.lower() for name in names), names


@pytest.mark.ui
def test_product_detail_shows_selected_name_and_price(page):
    """Goal: confirm product detail matches the selected product.
    Precondition: Claw Hammer is available in the catalog.
    Expected: detail page shows its name and a positive price."""
    product = HomePage(page).open().open_product("Claw Hammer")
    expect(product.name).to_have_text("Claw Hammer")
    assert product.price() > 0


@pytest.mark.ui
def test_empty_login_form_shows_required_field_errors(page):
    """Goal: validate required login fields.
    Precondition: login form is open and empty.
    Expected: required errors appear for email and password."""
    login = LoginPage(page).open()
    login.submit_button.click()
    expect(login.email_error).to_contain_text("Email is required")
    expect(login.password_error).to_contain_text("Password is required")


@pytest.mark.ui
def test_account_page_reuses_saved_login_state(logged_in_page):
    """Goal: open account using saved storage state.
    Precondition: session authentication state was created once.
    Expected: account page and signed in user menu are visible."""
    account = AccountPage(logged_in_page).open()
    expect(account.title).to_have_text("My account")
    expect(account.nav_menu).to_contain_text("QA Bot")


@pytest.mark.ui
def test_cart_continue_shopping_returns_to_product_list(page):
    """Goal: continue shopping from the cart.
    Precondition: a product has been added to a fresh cart.
    Expected: the product list is visible after navigation."""
    cart = HomePage(page).open().open_product("Claw Hammer").add_to_cart().go_to_cart()
    cart.continue_shopping.click()
    expect(HomePage(page).product_names.first).to_be_visible()
