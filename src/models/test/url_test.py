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
        ("htx://blog.monzo.com/"),
    ],
)
def test_url_address(test_address):
    """
    Simply verify that the URL address is as expected

    Args:
        test_address (str): test address for URL
    """
    assert URL(test_address).address == test_address


@pytest.mark.parametrize(
    "first_url, second_url, expected_equality",
    [
        (URL("https://www.google.com/a/b"), URL("https://www.google.com/a/b"), True),
        (
            URL("https://www.google.com/a/b"),
            URL("https://www.google.com/a/b#frag"),
            True,
        ),
        (
            URL("https://www.google.com/a/b#frag1"),
            URL("https://www.google.com/a/b#frag2"),
            True,
        ),
        (URL("https://www.google.com/a/b"), URL("https://www.google.com/b/"), False),
        (URL("https://www.google.com/a/b"), "https://www.google.com/a/b", False),
        (URL("https://www.monzo.com/a/b"), URL("https://www.google.com/a/b"), False),
    ],
)
def test_url_hash(first_url, second_url, expected_equality):
    """
    Verify that two URLs are considered duplicate when hashed into a set
    in case they are both URL objects and have the same address hash.

    Args:
        test_address (str): test address for URL
    """
    set_ = set()
    set_.add(first_url)
    set_.add(second_url)

    assert (len(set_) == 1) == expected_equality


@pytest.mark.parametrize(
    "test_address, is_valid_expected",
    [
        ("https://www.google.com/a/b", True),
        ("https://monzo.com/x", True),
        ("https://blog.monzo.com#frag/", True),
        ("htx://blog.monzo.com/", False),
        ("no-prefix.blog.monzo.com/", False),
        ("mailto:ihab@gmail.com", False),
    ],
)
def test_url_valid(test_address, is_valid_expected):
    """
    Test that a URL is valid based on having a valid subdomain
    and belonging to an http/https scheme.

    Args:
        test_address (str): test address for URL
    """
    assert URL(test_address).is_valid == is_valid_expected
