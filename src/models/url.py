"""URL Model"""
from urllib.parse import urlparse, urldefrag


class URL:
    """
    Utility class to process different parts of an http address.
    """

    class URLScheme:
        """Types of assumed URL schemes"""

        HTTP = "http"
        HTTPS = "https"

    def __init__(self, address: str) -> None:
        """
        Initialize the URL with a given address.
        When initializing a URL, any fragment is ignored, as it points
        to the same web-page.

        Args:
            address (address): address for the URL
        """
        defraged_url = urldefrag(address)
        parsed_url = urlparse(defraged_url.url)
        self._address = parsed_url.geturl()
        self._subdomain = parsed_url.hostname
        self._address_scheme = parsed_url.scheme

    @property
    def subdomain(self) -> str | None:
        """Returns parsed subdomain of URL

        Returns:
            str: subdomain
        """
        return self._subdomain

    @property
    def address(self) -> str:
        """
        Returns address for URL.

        Returns:
            string: address
        """
        return self._address

    @property
    def is_valid(self) -> str:
        """
        Returns whether or not a link is valid based on predefined criteria.
        For this web-crawler, a link is considered valid if it has a subdomain
        and an http/https scheme.

        Returns:
            string: address
        """

        return self._subdomain is not None and self._address_scheme in {
            URL.URLScheme.HTTP,
            URL.URLScheme.HTTPS,
        }

    def __repr__(self) -> str:
        return f"URL[{self.address}]"

    def __hash__(self) -> int:
        return self.address.__hash__()

    def __eq__(self, __o: object) -> bool:
        return isinstance(__o, URL) and self.address == __o.address
