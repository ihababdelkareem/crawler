"""Main HTML parsing functionality"""

from urllib.parse import urlparse
from urllib.error import HTTPError
import re
import urllib.request
from bs4 import BeautifulSoup

class URL:
    """
    Utility class to process different parts of an http address.
    """
    def __init__(self, address) -> None:
        """Initialize the URL with a given address

        Args:
            address (address): http address for the URL
        """
        self._address = address
        self._subdomain = None

    @property
    def subdomain(self) -> str:
        """Returns subdomain for URL.

        Returns:
            str: subdomain
        """
        if not self._subdomain:
            hostname = urlparse(self._address).hostname
            if hostname:
                self._subdomain =  hostname.split('.')[0]
            else:
                print(f'Unable to extract hostname for {self.address}')
        return self._subdomain

    @property
    def address(self) -> str:
        """
        Returns address for URL.

        Returns:
            string: address
        """
        return self._address

    def __repr__(self) -> str:
        return f"URL[{self.address}]"

    def __hash__(self) -> int:
        return self.address.__hash__()

    def __eq__(self, __o: object) -> bool:
        return isinstance(__o, URL) and self.address == __o.address
      

class HTMLParser:
    """ Parser class to handle fetching the related urls under a url's html page."""

    @staticmethod
    def get_links_under_url(url: URL) -> list[URL]:
        """Returns a list of URL objects found under the HTML page of a source url.

        Args:
            url (URL): Source URL for HTML page.

        Returns:
            list[URL]: List of URLs found in the source URL's page.
        """
        try:
            html_page = urllib.request.urlopen(url.address)
        except (ValueError, HTTPError) as parsing_exception:
            print(f'Unable to parse page for {url}: {parsing_exception}')
            return []

        soup = BeautifulSoup(html_page, "html.parser")
        linked_urls = []
        for address in soup.findAll('a', attrs={'href': re.compile("^https?://")}):
            linked_urls.append(URL(address.get('href')))
        return linked_urls
