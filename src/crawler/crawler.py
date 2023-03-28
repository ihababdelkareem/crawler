"""Functionality for the cralwer worker threads"""

from threading import Thread
from logger.logger import Logger
from models.url import URL
from repository.repository import Repository
from service.parser_service import HTMLParserService


class CrawlerOptions:
    """
    A class to control flags for the run of the crawler worker
    """

    def __init__(self, base_url_hostname: str, skip_links_found) -> None:
        self.skip_links_found = skip_links_found
        self.base_url_hostname = base_url_hostname


class Crawler(Thread):
    """
    Main crawler thread worker class. While running, the thread indefinetely polls
    for new links to be processed from the repository until there are no more
    links to be processed, after which it is expected to receive TERMINATION_SIGNAL
    in order to terminate.
    """

    # Used as a signal to terminate crawler workers
    TERMINATION_SIGNAL = URL("")

    def __init__(
        self,
        thread_id: int,
        repository: Repository,
        html_parser: HTMLParserService,
        options: CrawlerOptions,
        logger: Logger,
    ) -> None:
        """
        Initialize worker thread with connection to repository and the starting url
        that is used to limit the search space to a certain subdomain.

        Args:
            thread_id (int): Unique id to identify the crawlere worker.
            repository (Repository): Repository that contains overall crawling context.
            html_parser (HTMLParserService): Service that returns links under a given URL.
            options (CrawlerOptions): Flags to control crawler behaviour.
            logger (Logger): Thread-safe logger.
        """
        super().__init__()
        self._thread_id = thread_id
        self._repository = repository
        self._html_parser = html_parser
        self._options = options
        self._logger = logger

    def crawl_next_url(self) -> bool:
        """
        Main crawling logic executed by worker threads.
        - Poll for next URL to be processed in the queue.
        - Add all of its valid (i.e. not visited previously, and matches base subdomain)
          to be crawled next.
        - Notify repository that a the discovered URL has been processed.
        - Terminate if received TERMINATION_SIGNAL.
        """
        url_to_crawl = self._repository.get_next_url()
        if url_to_crawl == Crawler.TERMINATION_SIGNAL:
            return False
        linked_urls = self._html_parser.get_links_under_url(url_to_crawl)
        message = f"Thread-{self._thread_id} is currently crawling: {url_to_crawl}\n"
        if not self._options.skip_links_found:
            message += "------ Found following URLs in page: \n"
            for linked_url in linked_urls:
                message += f"------ {linked_url}\n"
        self._logger.log(message)
        for linked_url in linked_urls:
            if (
                linked_url.is_valid
                and linked_url.subdomain == self._options.base_url_hostname
            ):
                self._repository.add_url_to_crawl(linked_url)
        self._repository.notify_url_processed()
        return True

    def run(self) -> None:
        """
        Execute crawling logic indefinely until termination.
        """
        while self.crawl_next_url():
            pass
