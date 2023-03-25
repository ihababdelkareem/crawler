"""URL model tests"""
import pytest

from models.url import URL


@pytest.mark.parametrize("test_address,expected_subdomain", [("https://www.google.com", "www"),
                                                             ("https://monzo.com",
                                                              "monzo"),
                                                             ("monzo.com", None),
                                                             ])
def test_url_subdomain(test_address, expected_subdomain):
    """Verify that subdomains are extraceted correctly

    Args:
        test_address (str): test address for URL
        expected_subdomain (str): URL subdomain
    """
    assert URL(test_address).subdomain == expected_subdomain
