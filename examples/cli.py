import logicoma
import click


@logicoma.crawler()
# Crawler has full integration with click...
@click.argument('links', nargs=-1)
@click.option('--limit', type=int, default=42)
# ... other click options
def crawler(links, limit):
    click.echo(links)
    yield from links


if __name__ == '__main__':
    crawler()
