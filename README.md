# Logicoma

Logicoma is Python package for creating simple web crawlers with as little code
as necessary. It aims to make simple web crawlers as quick as possible.

*If some complex crawling is needed, this package may not be the right choice,
[Scrapy](https://scrapy.org/) or something else could be better choice.*


## Example

Download images or even entire galleries from [Imgur](https://imgur.com/):

```python
import click
import logicoma

crawler = logicoma.Crawler()

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

@click.command()
@click.option('-c', '--count', type=int, default=1, help='Number of threads')
@click.argument('links', nargs=-1)
def cli(**kwargs):
    crawler.start(**kwargs)

if __name__ == '__main__':
    cli()
```

Exmples with comments are in the `examples` directory.


## Installation

Clone repository

```
git clone https://github.com/fpob/logicoma
cd logicoma
```

and install Python package including dependencies

```
python3 setup.py install
```

### Recommended packages

* [click](http://click.pocoo.org/5/) - package for creating command line interfaces
* [browsercookie](https://pypi.org/project/browsercookie/) - loads cookies used by web browser
