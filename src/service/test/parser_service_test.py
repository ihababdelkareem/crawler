"""Parser service tests"""

from unittest.mock import MagicMock, Mock
import pytest
from requests import RequestException
from models.url import URL
from service.parser_service import HTMLParserService

TEST_URL_WITH_REFS = URL("https://monzo-links.com")
HTML_PAGE_WITH_REFS = """
<!DOCTYPE html>
<html>
<body>
<p>
Some link: <a href="https://www.monzo.com/a">
Some other link: <a href="https://www.facebook.com/b">
<img border="0" alt="W3Schools" src="logo_w3s.gif" width="100" height="100">
<div>
Some third link: <a href="http://www.hello-world.com">
Some forth link: <a href="http://www.monzo.com/a?q=hi">
</div>
</a>
</p>
</body>
</html>
"""

TEST_URL_WITHOUT_REFS = URL("https://monzo-no-links.com")
HTML_PAGE_WITHOUT_REFS = """
<!DOCTYPE html>
<html>
<body>
<p>
<img border="0" alt="W3Schools" src="logo_w3s.gif" width="100" height="100">
<div>
</div>
</a>
</p>
</body>
</html>
"""


def _get_mocked_http_response(test_address):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = (
        HTML_PAGE_WITH_REFS
        if test_address == TEST_URL_WITH_REFS.address
        else HTML_PAGE_WITHOUT_REFS
    )
    return mock_response


@pytest.mark.parametrize(
    "test_url,expected_urls",
    [
        (
            TEST_URL_WITH_REFS,
            [
                URL("https://www.monzo.com/a"),
                URL("https://www.facebook.com/b"),
                URL("http://www.hello-world.com"),
                URL("http://www.monzo.com/a?q=hi"),
            ],
        ),
        (TEST_URL_WITHOUT_REFS, []),
    ],
)
def test_links_under_url_returned(mocker, test_url, expected_urls):
    """
    Test that the parser service correctly returns
    the right number of links when HTML contains href tags
    """
    mocker.patch("requests.get", side_effect=_get_mocked_http_response)
    service = HTMLParserService(Mock())
    urls = service.get_links_under_url(test_url)
    assert urls == expected_urls


def test_links_returned_after_error(mocker):
    """
    Test that the parser service returns no links upon an exception
    being raised when fetching a page for a URL
    """
    mocker.patch(
        "requests.get",
        side_effect=RequestException("Failed to fetch page"),
    )
    service = HTMLParserService(Mock())
    urls = service.get_links_under_url(TEST_URL_WITH_REFS)
    assert len(urls) == 0


def test_links_returned_after_unsuccesful_html_page(mocker):
    """
    Test that the parser service returns no links upon fetching a web-page
    with a non-200 status page. Even if a page returns hyperlinks, we'd like
    to skip pages with errors like [404: Not found] of [403: Forbidden].
    """
    mocked_unsuccesful_response = MagicMock()
    mocked_unsuccesful_response.status_code = 403
    mocked_unsuccesful_response.text = HTML_PAGE_WITH_REFS
    mocker.patch(
        "requests.get",
        return_value=mocked_unsuccesful_response,
    )
    service = HTMLParserService(Mock())
    urls = service.get_links_under_url(TEST_URL_WITH_REFS)
    assert len(urls) == 0
