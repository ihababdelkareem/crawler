"""Logic to start crawling threads and initialize storage layer"""
from crawler.crawler import Crawler
from logger.logger import Logger
from models.options import CrawlerOptions
from repository.repository import Repository
from service.parser_service import HTMLParserService


class CrawlerLauncher:
    """
    Class to initialize crawler dependencies,
    mainly the worker threads and repository required for crawling.
    """

    def __init__(self, options: CrawlerOptions) -> None:
        self.options = options

    def terminate_all_workers(self, threads: list[Crawler],
                              thread_count: int,
                              repository: Repository) -> None:
        """
        Terminate all worker threads by sending a TERMINATION_SIGNAL.

        Args:
            threads (list[Crawler]): List of all active worker threads.
            thread_count (int): number of worker threads.
            repository (Repository): Repository used to enqueue URLs
        """
        for _ in range(thread_count):
            repository.queue_next_url(Crawler.TERMINATION_SIGNAL)
        for thread_index in range(thread_count):
            threads[thread_index].join()

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
        service = HTMLParserService()
        logger = Logger()
        repository.add_url_to_crawl(self.options.base_url)
        thread_count = self.options.thread_count
        threads = []
        for _ in range(thread_count):
            thread = Crawler(repository, service,
                             self.options, logger)
            thread.start()
            threads.append(thread)
        repository.wait_until_urls_processed()
        self.terminate_all_workers(threads, thread_count, repository)
        return repository.visited_urls
