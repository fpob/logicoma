import logicoma
import click


@logicoma.crawler()
# Crawler has full integration with click...
@click.argument('links', nargs=-1)
def crawler(links):
    # Crawler function have to return initial links, where crawling will start.
    return links


# Register handler for Imgur galleries. Pattern is matched with `re.search`.
@crawler.handler(r'//imgur\.com/')
def imgur_gallery(client, url):
    # Do a GET request to the url and parse response text. Parser is
    # BeautifulSoup.
    response, page = client.get_page(url)
    # Parse page...
    images = page.find(class_='post-images').find_all('a', class_='zoom')
    for img in images:
        img_url = logicoma.url_join(url, img.get('href'))
        # Yield next task to process. logicoma.Download is special task for
        # downloading files. File name is automacally parsed from the URL.
        yield logicoma.Download(img_url)
        # File name can be alternatively created manually and passed via data
        # argument. To simplify working with files there are some utils:
        # logicoma.url_filename() and logicoma.url_fileext().
        #yield logicoma.Download(img_url, {'filename': 'image.jpg'})


# Register handler for Imgur images.
@crawler.handler(r'//i\.imgur\.com/')
def imgur_image(url):
    # This is itself download file so just yield task to dowload this file.
    yield logicoma.Download(url)


if __name__ == '__main__':
    crawler()
