"""Crawler launcher tests"""

from crawler.launcher import CrawlerLauncher, CrawlerLauncherOptions
from models.url import URL


def mock_links_under_url(url):
    """
    Mimics a web page and the links it redirects to.
    In this simple example, the explored pages are
    [website.com -> website.com/a -> website.com/b -> website.com/xyz ->
    website.com/a/c -> website.com/a/d -> website.com/a/w]
    Args:
        url (URL): url to use to get linked urls
    """
    mock_pages = {
        URL("https://website.com"): {
            URL("https://website.com/a"),
            URL("https://website.blog.com/"),  # Not explored, different subdomain
            URL(
                "localhost://website.com/local"
            ),  # Not explored, invalid address scheme (not http/https)
            URL("https://website.com/b"),
            URL("https://website.com/xyz"),
            URL("https://a.xyz"),
            URL("https://abc.xyz"),
        },
        URL("https://website.com/a"): {
            URL("https://website.com/a/c"),
            URL("https://website.com/a/d"),
            URL("https://website.com/xyz"),
            URL("https://a.xyz"),
            URL("https://abc.xyz"),
        },
        URL("https://website.com/b"): {
            URL("https://website.com/a/c"),
            URL("https://website.com/a/w"),
            URL("https://website.com/xyz"),
            URL("https://a.xyz"),
            URL("https://abc.xyz"),
        },
    }

    # return an empty list if we the page is empty for a URL for any reason.
    # e.g. when crawling `website.a.w`, return an empty set.
    return mock_pages.get(url, set())


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
        base_url=URL("https://website.com"), skip_links_found=False, thread_count=4
    )

    # Execute crawler launcher
    visited_urls = CrawlerLauncher(options).crawl()

    # Assert that the crawled URLs are as expected
    assert set(visited_urls) == {
        URL("https://website.com/a"),
        URL("https://website.com/b"),
        URL("https://website.com/xyz"),
        URL("https://website.com/a/c"),
        URL("https://website.com/a/w"),
        URL("https://website.com/a/d"),
        URL("https://website.com"),
    }


def test_crawler_launcher_wth_invalid_url(mocker):
    """
    Test that the crawler returns an empty list of URLs in case it is
    seeded with an invalid URL.
    """

    # Set up crawler service to return set of URLs for each page
    mocker.patch(
        "crawler.launcher.HTMLParserService.get_links_under_url",
        side_effect=mock_links_under_url,
    )

    # Set up options to use a base URL and certain thread count
    options = CrawlerLauncherOptions(
        base_url=URL("htx://invalid.com"), skip_links_found=False, thread_count=4
    )

    # Execute crawler launcher
    visited_urls = CrawlerLauncher(options).crawl()

    # Assert that the crawled URLs are as expected
    assert not visited_urls
