"""Crawler launcher tests"""

from crawler.launcher import CrawlerLauncher
from models.options import CrawlerOptions
from models.url import URL


def mock_links_under_url(url):
    """
    Mimics a web page and the links it redirects to.
    In this simple example, the explored pages are
    [monzo.com -> monzo.a.a -> monzo.a.b -> monzo.xyz -> monzo.a.c -> monzo.a.d -> monzo.a.w]
    Args:
        url (URL): url to use to get linked urls
    """
    mock_pages = {URL('https://monzo.com'): [URL('https://monzo.a.a'),
                                             URL('https://monzo.a.b'),
                                             URL('https://monzo.xyz'),
                                             URL('https://a.xyz'),
                                             URL('https://abc.xyz')],
                  URL('https://monzo.a.a'): [URL('https://monzo.a.c'),
                                             URL('https://monzo.a.d'),
                                             URL('https://monzo.xyz'),
                                             URL('https://a.xyz'),
                                             URL('https://abc.xyz')],
                  URL('https://monzo.a.b'): [URL('https://monzo.a.c'),
                                             URL('https://monzo.a.w'),
                                             URL('https://monzo.xyz'),
                                             URL('https://a.xyz'),
                                             URL('https://abc.xyz')], }

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
        'crawler.launcher.HTMLParserService.get_links_under_url',
        side_effect=mock_links_under_url
    )

    # Set up options to use a base URL and certain thread count
    options = CrawlerOptions(base_url=URL(
        'https://monzo.com'), skip_links_found=False, thread_count=4)

    # Execute crawler launcher
    visited_urls = CrawlerLauncher(options).crawl()

    # Assert that the crawled URLs are as expected
    assert set(visited_urls) == set([URL('https://monzo.a.a'), URL('https://monzo.a.b'),
                                     URL('https://monzo.xyz'), URL('https://monzo.a.c'),
                                     URL('https://monzo.a.w'), URL('https://monzo.a.d'),
                                     URL('https://monzo.com')])
