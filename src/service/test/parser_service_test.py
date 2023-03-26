"""Parser service tests"""

import pytest
from models.url import URL
from service.parser_service import HTMLParserService
from urllib.error import URLError

HTML_PAGE_WITH_REFS = """
<!DOCTYPE html>
<html>
<body>
<p>
Some link: <a href="https://www.link.com">
Some other link: <a href="https://www.link.com">
<img border="0" alt="W3Schools" src="logo_w3s.gif" width="100" height="100">
<div>
Some third link: <a href="https://www.link.com">
</div>
</a>
</p>
</body>
</html>
"""

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

TEST_URL = URL('https://monzo.com')


@pytest.mark.parametrize("test_page,expected_link_count",
                         [(HTML_PAGE_WITH_REFS, 3),
                          (HTML_PAGE_WITHOUT_REFS, 0)])
def test_links_under_url_returned(mocker, test_page, expected_link_count):
    """
    Test that the parser service correctly returns 
    the right number of links when HTML contains href tags
    """
    mocker.patch(
        'urllib.request.urlopen',
        return_value=test_page
    )
    service = HTMLParserService()
    urls = service.get_links_under_url(TEST_URL)
    assert len(urls) == expected_link_count


def test_links_returned_after_error(mocker):
    """
    Test that the parser service returns no links upon an exception 
    being raised when fetching a page for a URL
    """
    mocker.patch(
        'urllib.request.urlopen',
        side_effect=URLError('Failed to fetch page'),
    )
    service = HTMLParserService()
    urls = service.get_links_under_url(TEST_URL)
    assert len(urls) == 0
