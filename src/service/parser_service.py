"""Main HTML parsing functionality"""

import requests
from bs4 import BeautifulSoup
from logger.logger import Logger

from models.url import URL


class HTMLParserService:
    """Parser class to handle fetching the related urls under a url's web-page."""

    HTTP_200 = 200

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
        html_page = None
        address = url.address
        try:
            html_page = requests.get(address)
        except requests.RequestException as request_exception:
            self._logger.log(
                f"Error while fetching web-page for {address}: [\n-----{request_exception}]",
                severity=Logger.Severity.ERROR,
            )
            return None

        http_status_code = html_page.status_code
        if http_status_code != HTMLParserService.HTTP_200:
            self._logger.log(
                f"Unsuccesful status code [{http_status_code}] returned"
                f" while fetching web-page for {address}",
                severity=Logger.Severity.ERROR,
            )
            return None
        return html_page.text

    def get_links_under_url(self, url: URL) -> list[URL]:
        """
        Returns a list of URL objects found under the HTML page of a source url.

        Args:
            url (URL): Source URL for HTML page.

        Returns:
            list[URL]: List of URLs found in the source URL's page.
        """

        html_page = self._get_url_html_page(url)
        if not html_page:
            return []

        soup = BeautifulSoup(html_page, "html.parser")
        linked_urls = []
        for address in soup.findAll("a"):
            linked_urls.append(URL(address.get("href")))
        return linked_urls
