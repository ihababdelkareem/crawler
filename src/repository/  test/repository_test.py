"""Test the repository layer of the web-crawler"""

from models.url import URL
from repository.repository import Repository


def test_repository_handles_redundancy():
    """Test that the repository handles rendunant links being added"""
    repository = Repository()

    repository.add_url_to_crawl(URL("test_0"))
    repository.add_url_to_crawl(URL("test_0"))
    repository.add_url_to_crawl(URL("test_1"))
    next_url_0 = repository.get_next_url()
    next_url_1 = repository.get_next_url()

    assert len(repository.visited_urls) == 2
    assert next_url_0 == URL("test_0")
    assert next_url_1 == URL("test_1")


def test_repository_unblocks_when_all_links_processed():
    """
    Test that the repository unblocks the caller when all
    previously enqueued URLs are reported as processed.
    """
    repository = Repository()

    repository.add_url_to_crawl(URL("test_0"))
    repository.add_url_to_crawl(URL("test_1"))
    next_url_0 = repository.get_next_url()
    repository.notify_url_processed()
    next_url_1 = repository.get_next_url()
    repository.notify_url_processed()

    repository.wait_until_urls_processed()

    assert len(repository.visited_urls) == 2
    assert next_url_0 == URL("test_0")
    assert next_url_1 == URL("test_1")
