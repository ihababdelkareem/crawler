"""Crawler launcher tests"""

from crawler.launcher import CrawlerLauncher, CrawlerLauncherOptions
from models.url import URL


def mock_links_under_url(url):
    """
    Mimics a web page and the links it redirects to.
    In this simple example, the explored pages are
    [monzo.com -> monzo.com/a -> monzo.com/b -> monzo.com/xyz ->
    monzo.com/a/c -> monzo.com/a/d -> monzo.com/a/w]
    Args:
        url (URL): url to use to get linked urls
    """
    mock_pages = {
        URL("https://monzo.com"): [
            URL("https://monzo.com/a"),
            URL("https://monzo.blog.com/"), # Not explored, different subdomain
            URL("localhost://monzo.com/local"), # Not explored, invalid address scheme (not http/https)
            URL("https://monzo.com/b"),
            URL("https://monzo.com/xyz"),
            URL("https://a.xyz"),
            URL("https://abc.xyz"),
        ],
        URL("https://monzo.com/a"): [
            URL("https://monzo.com/a/c"),
            URL("https://monzo.com/a/d"),
            URL("https://monzo.com/xyz"),
            URL("https://a.xyz"),
            URL("https://abc.xyz"),
        ],
        URL("https://monzo.com/b"): [
            URL("https://monzo.com/a/c"),
            URL("https://monzo.com/a/w"),
            URL("https://monzo.com/xyz"),
            URL("https://a.xyz"),
            URL("https://abc.xyz"),
        ],
    }

    # return an empty list if we the page is empty for a URL for any reason.
    # e.g. when crawling `monzo.a.w`, return []
    return mock_pages.get(url, [])


def test_crawler_launcher(mocker):
    """
    Test a simple crawling scenario with a mock web consisting of a predefined
    mapping of URLs to pages found under that URL
    """

    # Set up crawler service to return set of URLs for each page
    mocker.patch(
        "crawler.launcher.HTMLParserService.get_links_under_url",
        side_effect=mock_links_under_url,
    )

    # Set up options to use a base URL and certain thread count
    options = CrawlerLauncherOptions(
        base_url=URL("https://monzo.com"), skip_links_found=False, thread_count=4
    )

    # Execute crawler launcher
    visited_urls = CrawlerLauncher(options).crawl()

    # Assert that the crawled URLs are as expected
    assert set(visited_urls) == set(
        [
            URL("https://monzo.com/a"),
            URL("https://monzo.com/b"),
            URL("https://monzo.com/xyz"),
            URL("https://monzo.com/a/c"),
            URL("https://monzo.com/a/w"),
            URL("https://monzo.com/a/d"),
            URL("https://monzo.com"),
        ]
    )
