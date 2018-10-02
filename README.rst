Logicoma
========

Logicoma is Python package for creating simple web crawlers with as little code
as necessary. It aims to make simple web crawlers as quick as possible.

If some complex crawling is needed, this package may not be the right choice,
`Scrapy <https://scrapy.org/>`_ or something else could be better choice.


Example
-------

Download images or even entire galleries from `Imgur <https://imgur.com/>`_:

.. code:: python

    import click
    import logicoma

    @logicoma.crawler()
    @click.argument('links', nargs=-1)
    def crawler(links):
        return links

    @crawler.handler(r'//imgur\.com/')
    def imgur_gallery(client, url):
        response, page = client.get_page(url)
        images = page.find(class_='post-images').find_all('a', class_='zoom')
        for img in images:
            img_url = logicoma.url_join(url, img.get('href'))
            yield logicoma.Download(img_url)

    @crawler.handler(r'//i\.imgur\.com/')
    def imgur_image(url):
        yield logicoma.Download(url)

    if __name__ == '__main__':
        crawler()

Exmples with comments are in the `examples` directory.


Documentation
-------------

``@logicoma.crawler()``

   Decorator to create crawler. Decorated function must return initial list of
   links where crawling will start.

   In following docs ``<crawler>`` refers to function decorated with this
   decorator.

``<crawler>.client``

   ``logicoma.Client`` instance. You may want change some attributes of this or
   create own client instance.

``<crawler>.push_task(task)``

   Add task to queue. Task must be string or ``logicoma.Task`` instance.

``@<crawler>.handler(pattern, flags=0, priority=0)``

   Decorator to register new handler, class or function. Arguments ``pattern``
   and ``flags`` are passed to ``re.match`` function which is used to select
   handler for current URL from the queue.

   Handlers are sorted by ``priority`` value. So generic handlers (eg.
   ``.*\.jpg$``) should have lower priority than more specific handlers (eg.
   ``imgur\.com/.*\.jpg$``) because both can be used to download ``.jpg``
   files but probably you want use that specific handler.

   Decorated function can (but not have to) accept following arguments

      * ``client`` - ``logicoma.Client`` HTTP client
      * ``url`` - URL
      * ``data`` - custom data passed to ``logicoma.Task``
      * ``groups`` - all (positional and named) ``re.match`` groups

   and return or yield new URL as string or ``logicoma.Task`` which will be
   added to queue.

``@<crawler>.filter()``

   Decorator to register queue filter. Decorator function must to accept one
   argument - URL and return True or False whether URL should be added to queue
   or not.

   Can decorate also classes. Then instance is created only once and
   ``__call__`` method is used for filtering. With class filters can be
   created stateful filter (eg. deduplication).

``logicoma.Task(url, data={}, priority=0, handler=None)``

   Default crawling task. Priority is used to sort tasks in the queue, higher
   number means higher priority.

   Data argument can contain custom data passed to handler function as ``data``
   argument.

   Handler argument can be used to force use of given handler. If None then
   handler is selected from list of registered handlers.

``logicoma.Stop(priority=-9999)``

   ``logicoma.Task`` to stop crawling if there is no other tasks process.

``logicoma.Abort(priority=9999)``

   ``logicoma.Task`` to abort processing of queue as soon as possible.

``logicoma.Download(url, data={})``

   ``logicoma.Task`` to download given file. Argument ``data`` is dict with
   arguments for ``Client.download`` - ``filename``, ``method``. If no file
   name is specified, then file name extracted from URL is used. Default method
   is ``GET``.

``logicoma.Client(self, working_dir='.', headers=None, cookies=None, requests_delay=0)``

   ``working_dir`` is directory where files will be downloaded. ``headers`` and
   ``cookies`` is dict with headers and cookies...

   If `requests_delay` is greater than 0 then every request is delayed by a
   specified number of seconds. Delay should be used to reduce the servers or
   network load.

``logicoma.Client.request(method, url, delay=0, **kwargs)``

   Do a HTTP request to the given url. Method argument is HTTP method (get,
   post, ...). All other keyword arguments are passed to the
   ``requrests.request`` function.

   Request are delayed when argument `delay` or `self.requests_delay` is
   greater than zero. Delay time equals `max(delay, self.requests_delay)`
   seconds.

``logicoma.Client.get(...)``, ``logicoma.Client.post(...)``

   Shortcut for ``logicoma.Client.request('GET', ...)`` and
   ``logicoma.Client.request('POST', ...)``.

``logicoma.Client.request_page(method, url, **kwargs)``

   Shortcut to do a HTTP request (``logicoma.Client.request`` method) and parse
   text response with BeautifulSoup.

   Returns tuple of response and parsed page. If request failed (response.ok is
   False) then tuple of response and None (instead of parsed page) is returned.

``logicoma.Client.get_page(...)``

   Shortcut for ``logicoma.Client.request_page('GET', ...)``.

``logicoma.Client.download(url, filename=None, method='GET', **kwargs)``

   Download file and returns its file name and size. If `filename` is None,
   then file name will be extracted from URL.


Installation
------------

Install it using pip ::

    pip3 install logicoma

or clone repository ::

    git clone https://github.com/fpob/logicoma
    cd logicoma

and install Python package including dependencies ::

    python3 setup.py install

Recommended packages
^^^^^^^^^^^^^^^^^^^^

* `browsercookie <https://pypi.org/project/browsercookie/>`_ - loads cookies used by web browser
