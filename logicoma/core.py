"""
This module defines core set of classes for the crawler.
"""

__all__ = ['Client', 'Task', 'Crawler']

import logging
import os
import queue
import re
import bisect
import threading
import inspect
import time
import requests
import bs4

from . import utils


logger = logging.getLogger(__name__)


class Client:
    """HTTP client."""

    USER_AGENT = 'Logicoma'

    def __init__(self, working_dir='.', headers=None, cookies=None,
                 requests_delay=0):
        """
        If `requests_delay` is greater than 0 then every request is delayed by
        a specified number of seconds. Delay should be used to reduce the
        servers or network load.
        """
        self.working_dir = working_dir
        self.session = requests.Session()
        self.session.headers = {'User-Agent': self.USER_AGENT}
        if headers:
            self.session.headers.update(headers)
        if cookies:
            self.session.cookies = cookies
        self.requests_delay = requests_delay

    def file(self, *filename, mkdir=False):
        """
        Get file path from file name in working directory. If parent
        directiories not exists and `mkdir` is True, then creates all
        directories.
        """
        filepath = os.path.join(self.working_dir, *filename)
        if mkdir:
            dirname = os.path.dirname(filepath)
            if not os.path.exists(dirname):
                os.makedirs(dirname)
        return filepath

    def request_delay(self, delay=0):
        """
        Method for delaying the requests. Real delay time is maximum from
        argument `delay` and class attribute `requests_delay`.
        """
        delay = max(self.requests_delay, delay)
        if delay > 0:
            logger.debug('Request delay %.1f seconds', delay)
            time.sleep(delay)

    def get(self, url, delay=0, **kwargs):
        """
        Do a GET request to the given URL.

        See: requests.get, request_delay()
        """
        self.request_delay(delay)
        return self.session.get(url, **kwargs)

    def post(self, url, delay=0, **kwargs):
        """
        Do a POST request to the given URL.

        See: requests.post, request_delay()
        """
        self.request_delay(delay)
        return self.session.post(url, **kwargs)

    def get_page(self, url, **kwargs):
        """
        Shortcut to do a GET request and parse text response.

        Returns tuple of response and parsed page. If request failed
        (response.ok is False) then tuple of response and None (instead of
        parsed page) is returned.

        See: get()
        """
        response = self.get(url, **kwargs)
        if response.ok:
            return response, bs4.BeautifulSoup(response.text, 'html5lib')
        return response, None

    def download(self, url, filename=None, **kwargs):
        """
        Download file and returns its filename and size. If `filename` is None,
        then file name will be extracted from URL.

        See: get()
        """
        size = 0
        if not filename:
            filename = utils.url_filename(url)
        with open(self.file(filename), 'wb') as f:
            response = self.get(url, stream=True, **kwargs)
            for chunk in response.iter_content(chunk_size=4096):
                size += len(chunk)
                if chunk:
                    f.write(chunk)
        return filename, size


class Task:
    """
    Crawling task.

    One task should do only one thing, one request, so handlers should be
    simple as possible. If more requests is needed to complete some job, then
    task can return (or yield) list of next tasks which will be processed
    separately.

    Handler is function or callable class with fully optional arguments. If
    function can't accept eg. argument `data` (is not in its parameters list)
    then handler will not be called with this argument.

    Priority is used to sort tasks in queue. Higher number means higher
    priority.

    Handler arguments:
        client -- instance of Client
        url -- from Task
        data -- from Task
        groups -- If handler is instance of Handler, then matched groups are
            passed via this argument, otherwise will be None.
            see: Handler.groups()
    """

    def __init__(self, url, data={}, handler=None, priority=0):
        self.url = url
        self.data = data
        self.handler = handler
        self.priority = priority

    def process(self, client, **kwargs):
        """Execute task if handler is not None."""
        if self.handler:
            args = {'client': client, 'url': self.url, 'data': self.data}
            if isinstance(self.handler, Handler):
                args['groups'] = self.handler.groups(self.url)
            else:
                args['groups'] = None
            args.update(kwargs)
            # Pass only args which handler can accept.
            return self.handler(**{k: v for k, v in args.items()
                                   if k in self._handler_args()})

    def _handler_args(self):
        """Returns list of handler's argument names."""
        if isinstance(self.handler, Handler):
            handler = self.handler.func
        else:
            handler = self.handler
        if inspect.isclass(handler):
            handler = handler.__call__
        signature = inspect.signature(handler)
        return [param.name for param in signature.parameters.values()
                if param.kind == param.POSITIONAL_OR_KEYWORD]

    def is_stop(self):
        """Returns True if task is stop task."""
        return self.url is None and self.handler is None

    @classmethod
    def stop(cls, priority=-1000):
        """Create stop task."""
        return cls(None, priority=priority)

    def __lt__(self, other):
        return self.priority > other.priority

    def __repr__(self):
        return '<{} {}>'.format(self.__class__.__name__, repr(self.url))


class TaskQueue(queue.PriorityQueue):
    """
    Priority queue for tasks, which guarantees that two tasks with the same
    priority are returned in the order they were added

    https://docs.python.org/3/library/heapq.html#priority-queue-implementation-notes
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._lock = threading.Lock()
        self._counter = 0

    def put(self, task):
        with self._lock:
            super().put((-task.priority, self._counter, task))
            self._counter += 1

    def get(self):
        return super().get()[-1]


class Handler:
    """
    Acts like function, but with attached RE pattern to check if some URL is
    intended to be processed by this function.

    Priorities are used to select correct handler, if URL could be processed by
    multiple handlers. Higher number means higher priority.

    Given `func` can be function or callable class. Class instance will be
    created before call.
    """

    def __init__(self, func, pattern, flags=0, priority=0):
        self.func = func
        self.pattern = re.compile(pattern, flags)
        self.priority = priority

    def match(self, url):
        """
        Check if the given URL matches to this handler.

        See: re.search()
        """
        return bool(self.pattern.search(url))

    def groups(self, url):
        """
        Returns all (including named) match groups in the given URL. Returns
        dict of groups if match was found, otherwise None.
        """
        match = self.pattern.search(url)
        if match:
            return utils.merge_dicts({0: match.group(0)},
                                     dict(enumerate(match.groups(), 1)),
                                     match.groupdict())

    def __call__(self, *args, **kwargs):
        if inspect.isclass(self.func):
            return self.func()(*args, **kwargs)
        return self.func(*args, **kwargs)

    def __lt__(self, other):
        return self.priority > other.priority

    def __repr__(self):
        return "<{} {} {}>".format(self.__class__.__name__,
                                   self.func.__name__,
                                   repr(self.pattern.pattern))


class HandlerList:
    """
    Collection of handlers.

    Handlers are ordered by their priority or order of their addition. When
    searching for match they are iterated in that order and first matching
    handler is returned.
    """

    def __init__(self, handlers=[]):
        self.handlers = []
        for handler in handlers:
            self.append(handler)

    def append(self, handler):
        """
        Add handler to collection at right position respecting its priority.
        """
        if not isinstance(handler, Handler):
            raise TypeError('handler must be instance of Handler')
        bisect.insort_right(self.handlers, handler)

    def find_match(self, url):
        """
        Find handler which matches to given URL. If no handler was found then
        returns None.

        Handlers are iterated in order and first matching handler is returned.
        """
        for handler in self:
            if handler.match(url):
                return handler

    def __iter__(self):
        return iter(self.handlers)

    def __repr__(self):
        return repr(self.handlers)


class Crawler:
    """
    Main class to create crawlers.

    Example::

        crawler = Crawler()

        @crawler.starter()
        def start():
            return ['https://google.com/']

        @crawler.handler(r'https?//google.com/.*')
        def google(client, url):
            print('Googling...', url)
            return []  # next tasks to process

        crawler.start()
    """

    def __init__(self, starter=None, handlers=None, queue_filters=None,
                 client=None):
        self.starter_fun = starter or (lambda links: links)
        self.handler_list = HandlerList(handlers or [])
        self.queue_filter_chain = utils.FilterChain(queue_filters or [])
        self.client = client or Client()
        self.queue = TaskQueue()
        self._stop_evt = threading.Event()

    def push_task(self, task):
        """
        Add task to the queue. Task can be instance of Task class or list of
        tasks. Tasks are ordered by their priority or order of their addition.
        """
        if isinstance(task, list):
            for t in task:
                self.push_task(task)
            return
        if not isinstance(task, Task):
            raise TypeError('task must be instance of Task')
        if not task.handler:
            task.handler = self.handler_list.find_match(task.url)
        if not task.handler:
            logger.info('%s empty handler', task)
            return
        if self.queue_filter_chain(task):
            self.queue.put(task)
            logger.info('%s queued', task)
        else:
            logger.info('%s filtered out', task)

    def _worker(self):
        while True:
            task = self.queue.get()
            if task.is_stop() or self._stop_evt.is_set():
                break
            try:
                logger.info('%s started', task)
                next_tasks = task.process(self.client)
                if next_tasks:
                    for next_task in next_tasks:
                        if isinstance(next_task, str):
                            next_task = Task(next_task)
                        self.push_task(next_task)
                logger.info('%s finished', task)
            except Exception as e:
                logger.info('%s failed', task)
                logger.error(e, exc_info=True)
            self.queue.task_done()

    def start(self, *args, count=1, **kwargs):
        """
        Start the crawling in given count of threads.

        All arguments except `count` are passed to the starter function.
        Default starter function accepts only one argument `links` with list of
        urls to initialize the queue.

        This function blocks until all tasks from starter and handlers will be
        processed.
        """
        threads = [threading.Thread(target=self._worker) for _ in range(count)]
        try:
            for t in threads:
                t.start()
            for task in self.starter_fun(*args, **kwargs):
                if isinstance(task, str):
                    # Default priority is 0. Tasks from starter should have
                    # lower priority than implicit (str) tasks from task
                    # handlers.
                    task = Task(task, priority=-1)
                self.push_task(task)
            for t in threads:
                self.queue.put(Task.stop())
                t.join()
        except KeyboardInterrupt as e:
            self._stop_evt.set()
            logger.info('Stop request received, waiting for threads...')
            for t in threads:
                if t.is_alive():
                    t.join()
            raise e

    def starter(self):
        """
        Decorator to register the starter function (or class). Multiple
        starters are not allowed, only the last defined one is used.

        If starter is a class then instance is created immediately after
        registering.
        """
        def decorator(func):
            if inspect.isclass(func):
                self.starter_fun = func()
            else:
                self.starter_fun = func
            return func
        return decorator

    def handler(self, *args, **kwargs):
        """
        Decorator to register the handler function (or class). Arguments are
        the same as for the Handler.

        If handler is class, new instance is created for every task before it's
        processing.
        """
        def decorator(func):
            handler = Handler(func, *args, **kwargs)
            self.handler_list.append(handler)
            return func
        return decorator

    def queue_filter(self):
        """
        Decorator to register the filter function. Multiple filters are
        chained. All registered functions must return True to add the task to
        the queue, otherwise the task will not be queued.

        If filter is a class then instance is created immediately after
        registering.
        """
        def decorator(func):
            if inspect.isclass(func):
                self.queue_filter_chain.append(func())
            else:
                self.queue_filter_chain.append(func)
            return func
        return decorator
