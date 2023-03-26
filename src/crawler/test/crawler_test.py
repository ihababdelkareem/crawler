"""Test for the crawler worker functionality"""

from unittest.mock import Mock
from crawler.crawler import Crawler
from logger.logger import Logger
from models.options import CrawlerOptions
from models.url import URL
from repository.repository import Repository
from service.parser_service import HTMLParserService


def test_crawler_run_with_next_url(mocker):
    """
    Test the normal scenario of a crawler worker requesting the next url from the queue.
    """
    # Set up mock html service and repo
    mock_html_service = mocker.patch(
        'crawler.crawler.HTMLParserService',
    )
    mock_repo = mocker.patch(
        'crawler.crawler.Repository'
    )
    mock_html_service.get_links_under_url.return_value = [
        URL('https://monzo.b.com'), URL('https://monzo.c.com'), URL('https://xyz.c.com')]
    options = CrawlerOptions(base_url=URL('https://monzo.com'))
    crawler_worker = Crawler(mock_repo, mock_html_service, options, Mock())

    # Execute call to fetch next_url
    next_url_status = crawler_worker.crawl_next_url()

    # Assert that next_url_status is True (Not a termination signal)
    # and that the expected two urls that match the base subdomain (monzo.b, monzo.c)
    # are added to be crawled next
    assert next_url_status is True
    assert mock_repo.get_next_url.call_count == 1
    assert mock_repo.notify_url_processed.call_count == 1
    assert mock_repo.add_url_to_crawl.call_count == 2

def test_crawler_run_with_termination_signal(mocker):
    """
    Test the case where a crawler worker is signaled to terminate.
    """
    # Set up mock html service and repo
    mock_html_service = mocker.patch(
        'crawler.crawler.HTMLParserService',
    )
    mock_repo = mocker.patch(
        'crawler.crawler.Repository'
    )
    mock_repo.get_next_url.return_value = Crawler.TERMINATION_SIGNAL
    mock_html_service.get_links_under_url.return_value = [
        URL('https://monzo.b.com'), URL('https://monzo.c.com'), URL('https://xyz.c.com')]
    options = CrawlerOptions(base_url=URL('https://monzo.com'))
    crawler_worker = Crawler(mock_repo, mock_html_service, options, Mock())

    # Execute call to fetch next_url
    next_url_status = crawler_worker.crawl_next_url()

    # Assert that next_url_status is False (due to a termination signal)
    # and that the expected no urls are added to the repository
    assert next_url_status is False
    assert mock_repo.get_next_url.call_count == 1
    assert mock_repo.notify_url_processed.call_count == 0
    assert mock_repo.add_url_to_crawl.call_count == 0
