import logicoma


crawler = logicoma.Crawler()


# Register starter, function which initialize queue with some tasks.
@crawler.starter()
def starter():
    # Yield initial task. Return value must be list or this function must be
    # iterator. Strings are automatically converted to logicoma.Task. If you
    # need change priority or specify handler, you must return logicoma.Task.
    yield 'https://google.com/?q=example'


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


if __name__ == '__main__':
    # Start crawler.
    crawler.start()
