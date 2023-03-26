"""Main module to trigger crawler and parse input arguments"""
import argparse
from crawler.launcher import CrawlerLauncher
from models.options import CrawlerOptions
from models.url import URL

MONZO_BASE_URL = 'https://monzo.com/'


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Crawler Arguments",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--thread_count",
                        help="Number of threads to user for crawler",
                        nargs='?',
                        type=int,
                        default=1)
    parser.add_argument("--base_url",
                        help="Base URL to contain crawler into a single subdomain",
                        nargs='?',
                        type=str,
                        default=MONZO_BASE_URL)
    parser.add_argument("--skip_links_found",
                        help="Flag to skip logging links found under each page",
                        action="store_true")
    args = parser.parse_args()
    config = vars(args)
    crawler_options = CrawlerOptions(base_url=URL(config[CrawlerOptions.BASE_URL]),
                                     thread_count=config[CrawlerOptions.THREAD_COUNT],
                                     skip_links_found=config[CrawlerOptions.SKIP_LINKS_FOUND])
    urls_crawled = CrawlerLauncher(crawler_options).crawl()
    print(f'Found {len(urls_crawled)} URLs')
