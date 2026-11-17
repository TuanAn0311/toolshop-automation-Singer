"""Sprint 2 user API validation and authentication tests."""
import pytest

from conftest import new_email, register_user, strong_password

pytestmark = pytest.mark.api


@pytest.mark.parametrize(
    ("path", "expected_status"),
    [("/users/me", 401), ("/products/does-not-exist", 404)],
)
def test_protected_or_missing_resource_returns_expected_4xx(api, path, expected_status):
    """Goal: verify unauthenticated and missing resource errors.
    Precondition: no authorization token is sent.
    Expected: protected and missing resources return their documented 4xx status."""
    response = api.get(path)
    assert response.status == expected_status, response.text()


def test_register_empty_body_returns_422_field_errors(api):
    """Goal: validate required registration fields.
    Precondition: the registration body is empty.
    Expected: 422 response includes email and password errors."""
    response = api.post("/users/register", data={})
    assert response.status == 422, response.text()
    errors = response.json()
    assert "email" in errors and "password" in errors


def test_users_me_with_token_returns_own_profile(api, auth_headers, test_user):
    """Goal: verify bearer token authentication.
    Precondition: a session user and access token are available.
    Expected: the profile belongs to the fixture user."""
    response = api.get("/users/me", headers=auth_headers)
    assert response.status == 200, response.text()
    assert response.json()["email"] == test_user["email"]


def test_status_returns_toolshop(api):
    """Goal: check API health.
    Precondition: API endpoint is configured.
    Expected: status endpoint names the Toolshop application."""
    response = api.get("/status")
    assert response.status == 200, response.text()
    assert response.json()["app_name"] == "Toolshop"
