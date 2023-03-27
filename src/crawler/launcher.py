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

    def _instantiate_crawler_workers(
        self,
        thread_count: int,
        repository: Repository,
        html_parser: HTMLParserService,
        crawler_options: CrawlerOptions,
        logger: Logger,
    ) -> list[Crawler]:
        """
        Sequentially instantiate crawler worker threads with their required dependencies to kick-off
        the web-crawler.

        Args:
            thread_count (int): Number of threads to instantiate
            repository (Repository): Main repository to state web-crawler context
            html_parser (HTMLParserService): Service to parse HTML pages of a URL
            crawler_options (CrawlerOptions): Options to control crawler functionality
            logger (Logger): Thread-safe logger

        Returns:
            list[Crawler]: List of crawler threads.
        """
        threads = []
        for thread_id in range(thread_count):
            thread = Crawler(
                thread_id, repository, html_parser, crawler_options, logger
            )
            thread.start()
            threads.append(thread)
        return threads

    def _terminate_crawler_workers(
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

    def crawl(self) -> list[URL]:
        """
        Sets up the overall crawling logic, mainly split into:
         - Initializing the crawler repository, responsible for storing explored URLs
           and URLs to be crawled next.
         - Starting worker threads to pick up URLs to crawl from the queue.
         - Await a signal from the queue which notifies that all previously
           queued URLs have been crawled.
         - Terminate crawler threads by sending a TERMINATION_SIGNAL, indicating that all threads
           are idle.

        Returns:
            list[URL]: List of all valid URLs (Matching the base URL subdomain) crawled
        """
        repository = Repository()
        logger = Logger()
        html_parser = HTMLParserService(logger)
        thread_count = self._options.thread_count

        # Terminate early in the case where the base url is invalid.
        if not self._options.base_url.is_valid:
            return []

        base_url_hostname = self._options.base_url.subdomain
        crawler_options = CrawlerOptions(
            skip_links_found=self._options.skip_links_found,
            base_url_hostname=base_url_hostname,
        )

        # Seed the web-crawler with the base url
        repository.add_url_to_crawl(self._options.base_url)

        # Initialize the crawler worker threads
        crawler_threads = self._instantiate_crawler_workers(
            thread_count, repository, html_parser, crawler_options, logger
        )

        # Block until receiving a signal that all URLs have been crawled
        # and terminate worker threads
        repository.wait_until_all_urls_processed()
        self._terminate_crawler_workers(crawler_threads, thread_count, repository)
        return repository.visited_urls
