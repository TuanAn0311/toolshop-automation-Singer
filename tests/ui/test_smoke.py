import re
from uuid import uuid4

import pytest
from playwright.sync_api import expect

from pages.contact_page import ContactPage
from pages.home_page import HomePage
from pages.login_page import LoginPage


@pytest.mark.smoke
@pytest.mark.ui
def test_search_pliers_shows_only_matching_products(page):
    """Mục tiêu: tìm kiếm sản phẩm theo từ khóa pliers.
    Điều kiện: mở trang chủ và chờ danh sách sản phẩm tải xong.
    Mong đợi: có kết quả và mọi tên sản phẩm đều chứa pliers.
    """
    home = HomePage(page).open().search("pliers")
    expect(home.search_completed).to_be_visible()
    expect(home.search_caption).to_contain_text("pliers")
    expect(home.product_names.first).to_be_visible()
    names = home.product_names.all_inner_texts()
    assert names, "Không có sản phẩm trong kết quả tìm kiếm"
    assert all("pliers" in name.lower() for name in names), names


@pytest.mark.smoke
@pytest.mark.ui
def test_add_three_claw_hammers_updates_cart_badge(page):
    """Mục tiêu: thêm ba sản phẩm Claw Hammer vào giỏ hàng.
    Điều kiện: Claw Hammer có sẵn và giỏ hàng ban đầu trống.
    Mong đợi: thêm thành công và badge giỏ hàng hiển thị 3.
    """
    product = HomePage(page).open().open_product("Claw Hammer")
    expect(product.name).to_have_text("Claw Hammer")
    product.add_to_cart(quantity=3)
    expect(product.toast).to_contain_text("Product added to shopping cart")
    expect(product.cart_quantity).to_have_text("3")


@pytest.mark.smoke
@pytest.mark.ui
def test_login_with_nonexistent_email_shows_error(page):
    """Mục tiêu: từ chối đăng nhập bằng thông tin không hợp lệ.
    Điều kiện: dùng email ngẫu nhiên chưa đăng ký, không dùng tài khoản chung.
    Mong đợi: hiện Invalid email or password và URL kết thúc /auth/login.
    """
    email = f"sprint1-nonexistent-{uuid4().hex}@example.com"
    login = LoginPage(page).open().login(email, "Wrong-Password-123!")
    expect(login.error).to_contain_text("Invalid email or password")
    expect(page).to_have_url(re.compile(r"/auth/login$"))


@pytest.mark.smoke
@pytest.mark.ui
def test_empty_contact_form_shows_required_errors(page):
    """Mục tiêu: kiểm tra các trường bắt buộc của form liên hệ.
    Điều kiện: mở Contact, để trống toàn bộ form rồi bấm Send.
    Mong đợi: hiện Subject is required và Message is required.
    """
    contact = ContactPage(page).open().submit()
    expect(contact.errors).to_contain_text(
        ["Subject is required", "Message is required"]
    )
