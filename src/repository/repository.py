"""Persistence layer to keep track of crawled URLs"""

from queue import Queue
from threading import Lock

from models.url import URL


class Repository:
    """
    Class that persists status of web-crawler.
    """

    def __init__(self) -> None:
        # Mutex that is held whenever a new URL is discovered.
        # This is to prevent multiple threads from writing the same url twice
        # to the queue, and that checks to the global visited set are thread safe,
        # and therefore ensuring that a URL is only processed by one thread.
        self._mutex = Lock()

        # Thread-safe queue that is used to store urls to be explored next.
        # Ensures that reader/writer threads are always syncronized.
        self._urls_to_visit = Queue()

        # A set to keep track of all URLs visited historically by the crawler.
        # Also used to prevent visiting the same URL multiple times.
        self._visited_urls = set()

    def queue_next_url(self, url: URL) -> None:
        """
        Add URL to the `_urls_to_visit` queue
        Args:
            url (URL): URL to be visited
        """
        self._urls_to_visit.put(url)

    def add_url_to_crawl(self, url: URL) -> None:
        """
        Add a newly discovered URL to the queue to be explored (i.e. parse it's HTML page).
        This can be done once we ensure that the URL had not been discovered previously.
        Mutex is used to syncronize between multiple threads attempting to write the new URL
        as discovered. Note that the initial check is not protected by the lock,
        as locking would not be required in the case that the URL is confirmed to be visited before.
        (See https://en.wikipedia.org/wiki/Double-checked_locking).

        Args:
            url (URL): Discovered URL.
        """

        if url not in self._visited_urls:
            with self._mutex:
                if url not in self._visited_urls:
                    self.queue_next_url(url)
                    self._visited_urls.add(url)

    def get_next_url(self) -> URL:
        """
        Retrieve next url to be processed from the url queue.
        Blocks until an item is available on the queue.

        Returns:
            URL: Next URL to be processed.
        """
        return self._urls_to_visit.get()

    @property
    def visited_urls(self) -> list[URL]:
        """
        Get visited URLs at the time of function call

        Returns:
            int: Number of visited URLs
        """
        visited_urls_ = []
        with self._mutex:
            visited_urls_ = list(self._visited_urls)
        return visited_urls_

    def notify_url_processed(self) -> None:
        """
        Notify the underlying queue that a URL picked off the queue has been processed.
        This is primarily used by the queue to maintain context around which previously
        enqueued items are still being processed.
        """
        self._urls_to_visit.task_done()

    def wait_until_all_urls_processed(self) -> None:
        """
        Block until all URLs that have been picked up from the queue were reported as processed,
        which indicates that are no further URLs to be crawled.
        """
        self._urls_to_visit.join()
