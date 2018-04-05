"""
Definitions of non-core but useful tasks.
"""

from .core import Task


class Download(Task):
    """
    Task for downloading files. Handler argument is ignored.

    `data` are passed to Client.download method as **kwargs.
    """

    def __init__(self, *args, **kwargs):
        kwargs['handler'] = self.download
        super().__init__(*args, **kwargs)

    def download(self, client, url, data):
        client.download(url, **data)
