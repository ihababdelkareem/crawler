"""Functionality for the cralwer worker threads"""

from threading import Thread
from logger.logger import Logger
from models.url import URL
from models.options import CrawlerOptions
from repository.storage import CrawlerStorageContext
from service.parser_service import HTMLParserService


class Crawler(Thread):
    """
    Main crawler thread worker class. While running, the thread indefinetely polls 
    for new links to be processed from the repository until there are new more
    links to be processed.
    """
    next_crawler_id = 0

    def __init__(self, repository: CrawlerStorageContext,
                 service: HTMLParserService,
                 base_url: URL, options: CrawlerOptions,
                 logger: Logger) -> None:
        """
        Initialize worker thread with connection to repository and the starting url
        that is used to limit the search space to a certain subdomain.


        Args:
            db (CrawlerStorageContext): Repository that contains overall crawling context.
            base_url (URL): Starting URL.
        """
        super().__init__()
        self._repository = repository
        self.service = service
        self._base_url = base_url
        self._id = Crawler.next_crawler_id
        self._options = options
        self.logger = logger
        Crawler.next_crawler_id += 1

    def run(self) -> None:
        """
        Main crawling logic executed by worker threads.
        Essentially, threads wait until there's a new url to process
        """
        while True:
            discovered_url = self._repository.get_next_url()
            linked_urls = self.service.get_links_under_url(discovered_url)
            url_message = f'Thread:{self._id}: {discovered_url}\n'
            if not self._options.skip_links_found:
                for linked_url in linked_urls:
                    url_message += f'------ {linked_url}\n'
            self.logger.log(url_message)
            for linked_url in linked_urls:
                if linked_url.subdomain == self._base_url.subdomain:
                    self._repository.add_url_to_crawl(linked_url)
            self._repository.notify_url_processed()
