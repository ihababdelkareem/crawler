"""Functionality for the cralwer worker threads"""

from threading import Thread
from storage import CrawlerStorageContext
from html_parser import HTMLParser, URL

class Crawler(Thread):
    """
    Main crawler thread worker class. While running, the thread indefinetely polls 
    for new links to be processed from the repository until there are new more
    links to be processed.
    """
    next_crawler_id = 0
    def __init__(self, repository: CrawlerStorageContext, base_url: URL) -> None:
        """
        Initialize worker thread with connection to repository and the starting url
        that is used to limit the search space to a certain subdomain.


        Args:
            db (CrawlerStorageContext): Repository that contains overall crawling context.
            base_url (URL): Starting URL.
        """
        super().__init__()
        self._repository = repository
        self._base_url = base_url
        self._id = Crawler.next_crawler_id
        Crawler.next_crawler_id += 1
   
    def run(self) -> None:
        """
        Main crawling logic executed by worker threads. Essentially, threads wait until there's a new url to process
        """
        while True:
            discovered_url = self._repository.get_next_url()
            linked_urls = HTMLParser.get_links_under_url(discovered_url)
            print(f'Thread:{self._id}: {discovered_url}')
            for linked_url in linked_urls:
                print(f'------ {linked_url}')
                if linked_url.subdomain == self._base_url.subdomain:
                    self._repository.add_url_to_crawl(linked_url)
            self._repository.commit()
