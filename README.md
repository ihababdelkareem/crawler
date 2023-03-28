# Web Crawler

This project is a simple web-crawler that explores all URLs found under the web-pages from a starting URL. It is constrained to a single subdomain, meaning that only links matching the subdomain of the starting link are explored. All links however that are found under a crawled web-page are logged. The crawler can be configured with options such as the `number of threads to use`, which `URL to start from`, and whether or not to `log all pages found under an explored URL`.

## Functionality

### Overview
In essence, multiple threads work in parallel to pull URLs from a shared queue of URLs to be visited, and then add more URLs to be visited next. Once a thread is able to obtain a URL from the shared queue, its corresponding web-page is parsed and URLs are extracted from that web-page; these URLs are then queued to be explored, under the condition that they haven't been added previously.

### Race Conditions
Race conditions are expected to occur in the case of multiple threads attempting to access and mutate a shared resource. In this web-crawler, race conditions are handled in the following scenarios:
- Multiple threads attempting to `get` or `put` to the shared queue at the same time, which is why a thread-safe Queue from the python standard library is used.
- Multiple threads attempting to check and mark the same URL to be explored next, which is why a lock is used in the repository.
- Multiple threads attempting to log statements at the same time, leading in unexpected std-out behaviour or intertwined log statements, which is also handled by a lock.

### Nature of URLs
As expected when parsing a web-page, we may encounter absolute URLs being referenced, such as https://monzo.com/ referencing https://monzo.com/contacts. Additionaly, we may encounter relative links, such as https://monzo.com/faq/ referencing
`/faq/2022`, which resolves to https://monzo.com/faq/2022. Both relative and absolute URLs are resolved and added to be explored in the URLs queue. Furthermore, URLs may contain fragments, e.g. `#fragment`, which point the web-browser to a specific location within the web-page. URL fragments are dropped, as they don't contribute to finding a completely new web-page, and therefore are considered to be duplicate with their original web-page. Finally, 
URL validity is assumed to be when a URL contains a valid subdomain, i.e. whenever it is extractable, and an HTTP/HTTP address scheme, for example, the address `mailto:ihab@gmail.com` is not valid, neither is `htxyz://gmail.com`.

### Termination
As more and more URLs are being explored from the threads, new URLs are enqueued at a high rate to be explored next. Theoritically, the program terminates once all previously added URLs have been picked up from the queue and processed. The queue can be polled by the main thread to check whenever this happens. Once this is established, a `Poisin Pill`/`Termination Singal` is sent to all of the threads to indicate that their crawling is over.

## Trade-offs and Other Design Considerations

### Crawler and Repository Design
There are multiple trade-offs that arise when designed a multi-component web-crawler, most of which revolve around the nature of the shared data stores that keep context of the overall web-crawler storage. 

For example, the use of a single queue among all crawler workers leads to fairness in distributing all the pages discovered among the workers; however, this also leads to a bottleneck as there is a higher frequency of attempts to consume and produce URLs to the same queue, which may limit latency due to lock contention. On the other hand, one might consider using a queue per worker, which would limit such bottleneck but may cause un-even load patterns on the crawler workers or the loss of signifant parts of the URLs in case a worker is to terminate abruptly. 

Another consideration that could be thought of differently is the method of termination of the web-crawler. The current termination policy depends on every crawler worker reporting that succesful processing of each item picked up from the URLs queue; however, this does not account for worker threads abruptly shutting down while processing a URL, which would cause an inconsistency in keeping track of all processed URLs.

Finally, a further consideration might be setting limitations to the web-crawler, which would include its operation within certain boundaries instead of exhaustively enumerating all pages within a certain subdomain. Such limitation include setting the maximum number of pages to crawl, the maximum depth to reach, or setting a time limit for the web-crawler. 

### URL handling
As discussed previously, URLs can take various shapes and forms to lead to a resource on a remote machine. In this project, a URL was considered **explorable** once it qualified within the format of `<http/https>:<host>`, while invalid URLs, say `mailto:ihab@gmail` were logged without being explored. This assumption may limit our search space for other types of URLs that may also return valid HTML content, e.g. direct host address `172.253.62.99`, valid addresses with omitted or different URL schemes, e.g. `www.facebook.com`. 

We may also explore the possibility of pruning our search space to avoid requesting content for pages that are likely not to return HTML despite having a valid URL, e.g. `https://hostname.com/file.pdf`, instead of considering this as a resource that has no references.

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
To run the unit tests for all packages, simply run `pytest` with an optional argument `--cov` for the test coverage report.

```
======================================================================================================================================== test session starts =========================================================================================================================================
platform linux -- Python 3.10.4, pytest-7.2.2, pluggy-1.0.0
rootdir: /workspaces/crawler
plugins: anyio-3.6.2, mock-3.10.0, cov-4.0.0
collected 12 items                                                                                                                                                                                                                                                                                   

src/crawler/test/crawler_test.py ..                                                                                                                                                                                                                                                            [ 16%]
src/crawler/test/launcher_test.py .                                                                                                                                                                                                                                                            [ 25%]
src/models/test/url_test.py ....                                                                                                                                                                                                                                                               [ 58%]
src/repository/  test/repository_test.py ..                                                                                                                                                                                                                                                    [ 75%]
src/service/test/parser_service_test.py ...                                                                                                                                                                                                                                                    [100%]

========================================================================================================================================= 12 passed in 0.19s =========================================================================================================================================
```
