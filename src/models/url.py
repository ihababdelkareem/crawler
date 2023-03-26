"""URL Model"""
from urllib.parse import urlparse


class URL:
    """
    Utility class to process different parts of an http address.
    """

    def __init__(self, address: str) -> None:
        """Initialize the URL with a given address

        Args:
            address (address): http address for the URL
        """
        self._address = address
        self._subdomain = self._init_subdomain()

    def _init_subdomain(self) -> str:
        """Parses subdomain for URL.

        Returns:
            str: subdomain
        """
        return urlparse(self._address).hostname

    @property
    def subdomain(self) -> str:
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

    def __repr__(self) -> str:
        return f"URL[{self.address}]"

    def __hash__(self) -> int:
        return self.address.__hash__()

    def __eq__(self, __o: object) -> bool:
        return isinstance(__o, URL) and self.address == __o.address
