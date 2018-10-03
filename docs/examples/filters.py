import re
import logicoma


@logicoma.crawler()
def crawler():
    # Generate some duplicit pages.
    for _ in range(100):
        yield 'https://example.com/'
    # Generate request to insecure pages.
    for _ in range(100):
        yield 'http://example.com/'


@crawler.handler(r'//example\.com/')
def example(url):
    print('Processing', url)


# Register function to filter out insecure request. Task will be added to queue
# only if all registered filters return True.
@crawler.queue_filter()
def filter_insecure(task):
    if re.match('http://', task.url):
        return False
    return True


# Register class as filter. If filter is class, then instance will be created
# only once immediately after registering so it is stateful filter.
@crawler.queue_filter()
class DuplicateFilter:
    def __init__(self):
        # List of urls which was already queued.
        self.items = set()

    def __call__(self, task):
        if task.url in self.items:
            return False
        self.items.add(task.url)
        return True


if __name__ == '__main__':
    # Thanks to filters, `https://example.com/` will be processed just once,
    # and insecure `http` pages will not be processed at all.
    crawler()
