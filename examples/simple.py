import logicoma


# Register starter, function which initialize queue with some tasks.
@logicoma.crawler()
def crawler():
    # Yield initial task. Return value must be list or this function must be
    # iterator. Strings are automatically converted to logicoma.Task. If you
    # need change priority or specify handler, you must return logicoma.Task.
    yield 'https://google.com/?q=example'
    yield 'https://duckduckgo.com/?q=example'


# Register handler for googling. Match groups are passed to handler in `groups`
# argument. Handler arguments are `client`, `url`, `data` and `groups`. All
# argument are optional, handler function may not accept all of them.
@crawler.handler(r'//google\.com/\?q=(?P<query>.*)$')
def googling(client, url, groups):
    # Do something...
    print('Googling...', groups['query'])
    # Fetch page. client is instance of Client which should be used to create
    # all requests, downloads, etc...
    #response = client.get(url)
    # ...


# New instance is created for every URL.
@crawler.handler(r'//duckduckgo\.com/\?q=(?P<query>.*)$')
class DuckDuckGo:
    def __init__(self):
        print('DuckDuckGo init')

    def __call__(self, client, url, groups):
        print('DuckDuckGo search...', groups['query'])


if __name__ == '__main__':
    # Start crawler.
    crawler()
