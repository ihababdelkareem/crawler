# Web Crawler

This project is a simple web-crawler that explores all URLs found under the web-pages found from a starting URL. It is constrained to a single subdomain, meaning that only links matching the subdomain of the starting link are explored. All links however that are found under a crawled web-page are logged. The crawler can be configured with options such as the `number of threads to use`, which `URL to start from`, and whether or not to `log all pages found under an explored URL`.

## Functionality

### Overview
In essence, multiple threads work in parallel to pull URLs from a shared queue of URLs to be visited, and then add more URLs to be visited next. Once a thread is able to obtain a URL from the shared queue, its corresponding web-page is parsed and URLs are extracted from that web-page; these URLs are then queued to be explored, under the condition that they haven't been added previously.

### Race Conditions
Race conditions are expected to occur in the case of multiple threads attempting to access and mutate a shared resource. In this web-crawler, race conditions are handled in the following scenarios:
- Multiple threads attempting to `get` or `put` to the shared queue at the same time, which is why a thread-safe Queue from the python standard library is used.
- Multiple threads attempting to check and mark the same URL to be explored next, which is why a lock is used in the repository.
- Multiple threads attempting to log statements at the same time, leading in unexpected std-out behaviour or intertwined log statements, which is also handled by a lock.

### Termination
As more and more URLs are being explored from the threads, new URLs are enqueued at a high rate to be explored next. Theoritically, the program terminates once all previously added URLs have been picked up from the queue and processed. The queue can be polled by the main thread to check whenever this happens. Once this is established, a `Poisin Pill`/`Termination Singal` is sent to all of the threads to indicate that their crawling is over.

## Running the Project
To run the crawler or tests, first ensure that you have Python3 (3.10+ recommended) on your machine. After which you may install the required dependnecies from `requirements.txt` by running `pip3 install requirements.txt`
### Crawler
After checking the prerequisites, you can simply start the crawler by running
```sh
python3 src/main.py [-h] [--thread_count [THREAD_COUNT]] [--base_url [BASE_URL]] [--skip_links_found]
```

Example:

```sh
python3 src/main.py --thread_count=4 --base_url==https://monzo.com
```

After which the activity of each thread will be logged. 

Example of logged output:

```
Thread:1 is crawling: URL[https://monzo.com/blog/2018/07/03/the-big-list-update/]
------ Found following URLs in page: 
...
------ URL[http://monzo.com/]
------ URL[https://monzo.com/blog/2018/05/22/making-monzo-better/]
------ URL[https://monzo.com/blog/2018/06/14/bill-tracker/]
------ URL[https://twitter.com/makingmonzo]
------ URL[https://twitter.com/makingmonzo?ref_src=twsrc%5Etfw]
------ URL[https://community.monzo.com]
...
```

### Tests
To run the unit tests for all packages, simply run `pytest` with an optional argument `--cov` to get the coverage report.

```
========================================================================= test session starts =========================================================================
platform linux -- Python 3.10.4, pytest-7.2.2, pluggy-1.0.0
rootdir: /workspaces/crawler
plugins: anyio-3.6.2, mock-3.10.0, cov-4.0.0
collected 11 items                                                                                                                                                    

src/crawler/test/crawler_test.py ..                                                                                                                             [ 18%]
src/crawler/test/launcher_test.py .                                                                                                                             [ 27%]
src/models/test/url_test.py ...                                                                                                                                 [ 54%]
src/repository/  test/repository_test.py ..                                                                                                                     [ 72%]
src/service/test/parser_service_test.py ...                                                                                                                     [100%]

---------- coverage: platform linux, python 3.10.4-final-0 -----------
Name                                       Stmts   Miss  Cover
--------------------------------------------------------------
src/crawler/__init__.py                        0      0   100%
src/crawler/crawler.py                        36      0   100%
src/crawler/launcher.py                       27      0   100%
src/crawler/test/__init__.py                   0      0   100%
src/crawler/test/crawler_test.py              30      0   100%
src/crawler/test/launcher_test.py             11      0   100%
src/logger/__init__.py                         0      0   100%
src/logger/logger.py                           7      0   100%
src/models/__init__.py                         0      0   100%
src/models/options.py                          9      0   100%
src/models/test/__init__.py                    0      0   100%
src/models/test/url_test.py                    5      0   100%
src/models/url.py                             23      0   100%
src/repository/__init__.py                     0      0   100%
src/repository/repository.py                  28      0   100%
src/repository/  test/repository_test.py      24      0   100%
src/service/__init__.py                        0      0   100%
src/service/parser_service.py                 18      0   100%
src/service/test/__init__.py                   0      0   100%
src/service/test/parser_service_test.py       18      0   100%
--------------------------------------------------------------
TOTAL                                        236      0   100%


========================================================================= 11 passed in 0.31s ==========================================================================

```
