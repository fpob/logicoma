import logicoma


@logicoma.crawler()
def crawler(urls):
    return urls


# To do something eg. on the facebook we need to be logged in...
@crawler.handler(r'//www\.facebook\.com/')
def facebook(client, url):
    pass


if __name__ == '__main__':
    # Create crawler client with cookies loaded from browser.
    import browsercookie
    crawler.client = logicoma.Client(cookies=browsercookie.load())

    crawler([])
