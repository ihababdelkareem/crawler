"""Main HTML parsing functionality"""

from urllib.error import HTTPError, URLError
import re
import urllib.request
from bs4 import BeautifulSoup

from models.url import URL


class HTMLParserService:
    """ Parser class to handle fetching the related urls under a url's web-page."""

    def __init__(self) -> None:
        pass

    def get_links_under_url(self, url: URL) -> list[URL]:
        """Returns a list of URL objects found under the HTML page of a source url.

        Args:
            url (URL): Source URL for HTML page.

        Returns:
            list[URL]: List of URLs found in the source URL's page.
        """
        try:
            html_page = urllib.request.urlopen(url.address)
        except (ValueError, HTTPError, URLError):
            return []

        soup = BeautifulSoup(html_page, "html.parser")
        linked_urls = []
        for address in soup.findAll('a', attrs={'href': re.compile("^https?://")}):
            linked_urls.append(URL(address.get('href')))
        return linked_urls
