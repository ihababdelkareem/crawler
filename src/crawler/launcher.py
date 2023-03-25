"""Logic to start crawling threads and initialize storage layer"""
from crawler.crawler import Crawler
from logger.logger import Logger
from models.options import CrawlerOptions
from repository.storage import CrawlerStorageContext
from service.parser_service import HTMLParserService


class CrawlerLauncher:
    """
    Class to initialize crawler dependencies,
    mainly the threads and repository required for crawling
    """

    def __init__(self, options: CrawlerOptions) -> None:
        self.options = options

    def crawl(self):
        """
        Sets up the overall crawling logic, mainly split into:
         - Initializing the crawler repository, responsible for storing explored URLs
           and URLs to be crawled next.
         - Starting worker threads to pick up URLs to crawl from the queue.
         - Await a signal from the queue which notifies that all previously
           queued URLs have been crawled.
         - Terminate main and crawler threads
        """
        repository = CrawlerStorageContext()
        service = HTMLParserService()
        logger = Logger()
        base_url = self.options.base_url
        repository.add_url_to_crawl(self.options.base_url)
        thread_count = self.options.thread_count
        threads = []
        for _ in range(thread_count):
            thread = Crawler(repository, service, base_url,
                             self.options, logger)
            thread.daemon = True
            thread.start()
            threads.append(thread)
        repository.wait_until_urls_processed()
