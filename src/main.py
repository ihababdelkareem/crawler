"""Main module to trigger crawler and parse input arguments"""
import argparse
from crawler.launcher import CrawlerLauncher, CrawlerLauncherOptions
from models.url import URL

BASE_URL = "https://www.lindushealth.com/"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Crawler Arguments",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--thread_count",
        help="Number of threads to user for crawler",
        nargs="?",
        type=int,
        default=1,
    )
    parser.add_argument(
        "--base_url",
        help="Base URL to contain crawler into a single subdomain",
        nargs="?",
        type=str,
        default=BASE_URL,
    )
    parser.add_argument(
        "--skip_links_found",
        help="Flag to skip logging links found under each page",
        action="store_true",
    )
    args = parser.parse_args()
    config = vars(args)
    crawler_launcher_options = CrawlerLauncherOptions(
        base_url=URL(config[CrawlerLauncherOptions.BASE_URL]),
        thread_count=config[CrawlerLauncherOptions.THREAD_COUNT],
        skip_links_found=config[CrawlerLauncherOptions.SKIP_LINKS_FOUND],
    )
    urls_crawled = CrawlerLauncher(crawler_launcher_options).crawl()
    print(f"Crawled {len(urls_crawled)} URL(s)")
