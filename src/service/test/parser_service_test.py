"""Parser service tests"""

from unittest.mock import MagicMock, Mock
import pytest
from requests import RequestException
from models.url import URL
from service.parser_service import HTMLParserService

TEST_URL_WITH_REFS = URL("https://monzo-links.com/faq/index.html")
HTML_PAGE_WITH_REFS = """
<!DOCTYPE html>
<html>
<body>
<p>
Other link: <a href="https://www.monzo.com/a">
Other link mentioned twice: <a href="https://www.monzo.com/a">
Other link w/fragment: <a href="https://www.monzo.com/a#frag">
Other link [2]: <a href="https://www.facebook.com/b">
Other link [2] w/fragment: <a href="https://www.facebook.com/b#other">
<img border="0" alt="W3Schools" src="logo_w3s.gif" width="100" height="100">
<div>
Other link [3]: <a href="http://www.hello-world.com">
Other link [4]: <a href="http://www.monzo.com/a?q=hi">
Relative link: <a href="relative.html">
Relative link [2]: <a href="/login">
Relative link [3]: <a href="/../"> 
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


class MockHTTPResponse(MagicMock):
    """Mocked HTTP response"""

    def __init__(self, status_code, text):
        super().__init__()
        self.status_code = status_code
        self.text = text

    @property
    def ok(self):
        return self.status_code < 400


def _get_mocked_http_response(test_address):
    mock_html_text = (
        HTML_PAGE_WITH_REFS
        if test_address == TEST_URL_WITH_REFS.address
        else HTML_PAGE_WITHOUT_REFS
    )
    mock_response = MockHTTPResponse(200, mock_html_text)
    return mock_response


@pytest.mark.parametrize(
    "test_url,expected_urls",
    [
        (
            TEST_URL_WITH_REFS,
            {
                URL("https://www.monzo.com/a"),
                URL("https://www.facebook.com/b"),
                URL("http://www.hello-world.com"),
                URL("http://www.monzo.com/a?q=hi"),
                URL("https://monzo-links.com/faq/relative.html"),
                URL("https://monzo-links.com/login"),
                URL("https://monzo-links.com/"),
            },
        ),
        (TEST_URL_WITHOUT_REFS, set()),
    ],
)
def test_links_under_url_returned(mocker, test_url, expected_urls):
    """
    Test that the parser service correctly returns
    the right number of links when HTML contains href tags.
    This includes checking for duplicated links (By fragments or duplication),
    and relative links that are resolved to their corresponding absolute links.
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
    mocked_unsuccesful_response = MockHTTPResponse(403, HTML_PAGE_WITH_REFS)
    mocker.patch(
        "requests.get",
        return_value=mocked_unsuccesful_response,
    )
    service = HTMLParserService(Mock())
    urls = service.get_links_under_url(TEST_URL_WITH_REFS)
    assert len(urls) == 0
