"""Logic to start crawling threads and initialize storage layer"""
from crawler.crawler import Crawler, CrawlerOptions
from logger.logger import Logger
from models.url import URL
from repository.repository import Repository
from service.parser_service import HTMLParserService


class CrawlerLauncherOptions:
    """
    A class to control flags for the run of the crawler launcher
    """

    THREAD_COUNT = "thread_count"
    SKIP_LINKS_FOUND = "skip_links_found"
    BASE_URL = "base_url"

    def __init__(
        self, base_url: URL, skip_links_found: bool = False, thread_count: int = 1
    ) -> None:
        self.skip_links_found = skip_links_found
        self.thread_count = thread_count
        self.base_url = base_url


class CrawlerLauncher:
    """
    Class to initialize crawler dependencies,
    mainly the worker threads and repository required for crawling.
    """

    def __init__(self, options: CrawlerLauncherOptions) -> None:
        self._options = options

    def _terminate_all_workers(
        self, threads: list[Crawler], thread_count: int, repository: Repository
    ) -> None:
        """
        Terminate all worker threads by sending a TERMINATION_SIGNAL.

        Args:
            threads (list[Crawler]): List of all active worker threads.
            thread_count (int): number of worker threads.
            repository (Repository): Repository used to enqueue URLs
        """
        for _ in range(thread_count):
            repository.queue_next_url(Crawler.TERMINATION_SIGNAL)
        for thread_id in range(thread_count):
            threads[thread_id].join()

    def crawl(self):
        """
        Sets up the overall crawling logic, mainly split into:
         - Initializing the crawler repository, responsible for storing explored URLs
           and URLs to be crawled next.
         - Starting worker threads to pick up URLs to crawl from the queue.
         - Await a signal from the queue which notifies that all previously
           queued URLs have been crawled.
         - Terminate crawler threads by sending a TERMINATION_SIGNAL, indicating that all threads
           are idle.
        """
        repository = Repository()
        html_parser = HTMLParserService()
        logger = Logger()
        repository.add_url_to_crawl(self._options.base_url)
        thread_count = self._options.thread_count
        base_url_hostname = self._options.base_url.subdomain
        crawler_options = CrawlerOptions(
            skip_links_found=self._options.skip_links_found,
            base_url_hostname=base_url_hostname,
        )
        threads = []
        for thread_id in range(thread_count):
            thread = Crawler(
                thread_id, repository, html_parser, crawler_options, logger
            )
            thread.start()
            threads.append(thread)
        repository.wait_until_urls_processed()
        self._terminate_all_workers(threads, thread_count, repository)
        return repository.visited_urls
