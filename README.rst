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
