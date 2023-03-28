"""Main HTML parsing functionality"""

from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
from logger.logger import Logger

from models.url import URL


class HTMLParserService:
    """Parser class to handle fetching the related urls under a url's web-page."""

    def __init__(self, logger: Logger) -> None:
        self._logger = logger

    def _get_url_html_page(self, url: URL) -> str | None:
        """
        Attempt to fetch the HTML page for a certain URL as string of bytes.

        Args:
            url (URL): Input URL.

        Returns:
            str | None: HTML markup if request is succesful,
            or None if error occurs.
        """
        html_page_response = None
        address = url.address
        try:
            html_page_response = requests.get(address)
        except requests.RequestException as request_exception:
            self._logger.log(
                f"Error while fetching web-page for {address}: [\n-----{request_exception}]",
                severity=Logger.Severity.ERROR,
            )
            return None

        # Fail if HTTP status code is not OK
        http_status_code = html_page_response.status_code
        http_status_ok = html_page_response.ok
        if not http_status_ok:
            self._logger.log(
                f"HTTP status code not OK [{http_status_code}] returned"
                f" while fetching web-page for {address}",
                severity=Logger.Severity.ERROR,
            )
            return None
        return html_page_response.text

    def get_links_under_url(self, url: URL) -> set[URL]:
        """
        Returns a set of URL objects found under the HTML page of a source url.
        There are multiple reasons why a URL might be duplicate in a web-page,
        such as it being referenced multiple times, or multiple fragments
        (monzo.com#this_tab, monzo.com#that_tab) being referenced for the same address.

        Args:
            url (URL): Source URL for HTML page.

        Returns:
            set[URL]: Set of URLs found in the source URL's page.
        """
        url_address = url.address
        html_page = self._get_url_html_page(url)
        if not html_page:
            return set()

        soup = BeautifulSoup(html_page, "html.parser")
        linked_urls = set()
        for address in soup.findAll("a"):
            parsed_address = address.get("href")
            # urljoin correctly handles absolute and relative paths.
            joined_address = urljoin(url_address, parsed_address)
            linked_urls.add(URL(joined_address))
        return linked_urls
