"""Flags to control web-crawler behaviour"""
from models.url import URL


class CrawlerOptions:
    """A class to control flags for the run of the crawler
    """
    THREAD_COUNT = 'thread_count'
    SKIP_LINKS_FOUND = 'skip_links_found'
    BASE_URL = 'base_url'

    def __init__(self, base_url: URL,
                skip_links_found: bool = False,
                thread_count: int = 1) -> None:
        self.skip_links_found = skip_links_found
        self.thread_count = thread_count
        self.base_url = base_url
