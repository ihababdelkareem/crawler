"""URL model tests"""
import pytest

from models.url import URL


@pytest.mark.parametrize(
    "test_address,expected_subdomain",
    [
        ("https://www.google.com/a/b", "www.google.com"),
        ("https://monzo.com/x", "monzo.com"),
        ("https://blog.monzo.com/", "blog.monzo.com"),
        ("monzo.com", None),
    ],
)
def test_url_subdomain(test_address, expected_subdomain):
    """
    Verify that subdomains are extraceted correctly

    Args:
        test_address (str): test address for URL
        expected_subdomain (str): URL subdomain
    """
    assert URL(test_address).subdomain == expected_subdomain


@pytest.mark.parametrize(
    "test_address",
    [
        ("https://www.google.com/a/b"),
        ("https://monzo.com/x"),
        ("https://blog.monzo.com/"),
    ],
)
def test_url_address(test_address):
    """
    Simply verify that the URL address is as expected

    Args:
        test_address (str): test address for URL
    """
    assert URL(test_address).address == test_address
