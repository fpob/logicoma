import logicoma
import click
import browsercookie


@logicoma.crawler()
@click.argument('links', nargs=-1)
def crawler(links):
    # Recreate crawler client with cookies loaded from browser.
    crawler.client = logicoma.Client(cookies=browsercookie.load())

    return links


# To do something eg. on the facebook we need to be logged in...
@crawler.handler(r'//www\.facebook\.com/')
def facebook(client, url):
    pass


if __name__ == '__main__':
    crawler()
