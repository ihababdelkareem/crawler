from crawler import Crawler
from storage import CrawlerStorageContext
from html_parser import URL

db = CrawlerStorageContext()
base_url = URL('https://monzo.com/')
db.add_url_to_crawl(base_url)
thread_count = 1
threads = []
for i in range(thread_count):
    thread = Crawler(db, base_url)
    thread.daemon = True
    thread.start()
    threads.append(thread)
db.wait_for_empty_queue()
print(len(db.visited_urls))
