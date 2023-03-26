"""Functionality for the cralwer worker threads"""

from threading import Thread
from logger.logger import Logger
from models.url import URL
from models.options import CrawlerOptions
from repository.repository import Repository
from service.parser_service import HTMLParserService


class Crawler(Thread):
    """
    Main crawler thread worker class. While running, the thread indefinetely polls
    for new links to be processed from the repository until there are new more
    links to be processed, after which it is expected to receive TERMINATION_SIGNAL 
    in order to terminate.
    """
    # Used as a signal to terminate crawler workers
    TERMINATION_SIGNAL = URL('')
    next_crawler_id = 0

    def __init__(self, repository: Repository,
                 service: HTMLParserService,
                 options: CrawlerOptions,
                 logger: Logger) -> None:
        """
        Initialize worker thread with connection to repository and the starting url
        that is used to limit the search space to a certain subdomain.

        Args:
            repository (Repository): Repository that contains overall crawling context.
            service (HTMLParserService): Service that returns links under a given URL.
            options (CrawlerOptions): Flags to control crawler behaviour.
            logger (Logger): Thread-safe logger.
        """
        super().__init__()
        self._repository = repository
        self._service = service
        self._id = Crawler.next_crawler_id
        self._options = options
        self._logger = logger
        Crawler.next_crawler_id += 1

    def crawl_next_url(self) -> bool:
        """
        Main crawling logic executed by worker threads.
        - Poll for next URL to be processed in the queue.
        - Add all of its valid (i.e. not visited previously, and matches base subdomain)
          to be crawled next.
        - Notify repository that a the discovered URL has been processed.
        - Terminate if received TERMINATION_SIGNAL.
        """
        discovered_url = self._repository.get_next_url()
        if discovered_url == Crawler.TERMINATION_SIGNAL:
            return False
        linked_urls = self._service.get_links_under_url(discovered_url)
        url_message = f'Thread:{self._id} is crawling: {discovered_url}\n'
        url_message += '------ Found following URLs in page: \n'
        if not self._options.skip_links_found:
            for linked_url in linked_urls:
                url_message += f'------ {linked_url}\n'
        self._logger.log(url_message)
        for linked_url in linked_urls:
            if linked_url.subdomain == self._options.base_url.subdomain:
                self._repository.add_url_to_crawl(linked_url)
        self._repository.notify_url_processed()
        return True

    def run(self) -> None:
        """
        Execute crawling logic indefinely until termination.
        """
        while self.crawl_next_url():
            pass
