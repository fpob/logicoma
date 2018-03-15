"""
Definitions of some helpers functions or classes to simplify working with
crawler and other things.
"""

__all__ = ['url_filename', 'url_fileext', 'url_replace', 'url_join',
           'sanitize', 'strip_white']

import urllib.parse
import unicodedata
import re
import os


def url_filename(url):
    """Extract file name from URL. Filename is last part (after /) of path."""
    return urllib.parse.urlparse(url).path.strip('/').split('/')[-1]


def url_fileext(url):
    """Extract file extension from URL."""
    return os.path.splitext(url_filename(url))[-1]


def url_replace(url, **kwargs):
    """
    Replace some part of URL.

    See: urllib.parse.urlparse
    """
    return urllib.parse.urlparse(url)._replace(**kwargs).geturl()


def url_join(base, *url):
    """
    Construct absolute url comibining `base` with another `url`. Url parts are
    before constructing joined with '/'.

    See: urllib.parse.urljoin
    """
    return urllib.parse.urljoin(base, '/'.join(url))


def sanitize(string, to_lower=True):
    """
    Sanitize string so it will contain only `a-zA-Z0-9` characters, all other
    characters will be replaced with dash.
    """
    asciized = unicodedata.normalize('NFKD', string).encode('ASCII', 'ignore')
    sanitized = re.sub(r'[^a-zA-Z0-9]+', '-',
                       asciized.decode('ASCII')).strip('-')
    return sanitized.lower() if to_lower else sanitized


def strip_white(string):
    """
    Remove all extra whitespaces from `string` and replace them with single
    space.
    """
    return re.sub(r'\s\s+', ' ', string.strip())


def merge_dicts(*dicts):
    """
    Copy and merge given dicts into a new dict, precedence goes to key value
    pairs in latter dicts.
    """
    result = {}
    for d in dicts:
        result.update(d)
    return result


class FilterChain(list):
    """
    Chain multiple filter functions into one with logical conjuction. Returns
    True if all filters returns True or chain is empty.
    """

    def append(self, item):
        """Append function to chain. This method can be used as decorator."""
        super().append(item)
        return item

    def __call__(self, value):
        for f in self:
            if not f(value):
                return False
        return True
