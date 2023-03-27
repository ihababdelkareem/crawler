"""URL Model"""
from urllib.parse import urlparse


class URL:
    """
    Utility class to process different parts of an http address.
    """

    HTTP = 'http'
    HTTPS = 'https'

    def __init__(self, address: str) -> None:
        """Initialize the URL with a given address

        Args:
            address (address): http address for the URL
        """
        self._address = address
        self._subdomain = None
        self._address_scheme = None
        self._parse_url()

    def _parse_url(self) -> str | None:
        """
        Parses subdomain and address for URL.
        """
        parsed_url = urlparse(self._address)
        self._subdomain = parsed_url.hostname
        self._address_scheme = parsed_url.scheme

    @property
    def subdomain(self) -> str | None :
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
        For this web-crawler, a link is considered valid if it has a valid 
        subdomain and an http/https scheme.

        Returns:
            string: address
        """
        return self._subdomain and self._address_scheme in {URL.HTTP, URL.HTTPS}

    def __repr__(self) -> str:
        return f"URL[{self.address}]"

    def __hash__(self) -> int:
        return self.address.__hash__()

    def __eq__(self, __o: object) -> bool:
        return isinstance(__o, URL) and self.address == __o.address
