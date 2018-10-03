"""
Definitions of non-core but useful tasks.
"""

import logging
import requests

from .core import Task


logger = logging.getLogger(__name__)


class Download(Task):
    """
    Task for downloading files. Handler argument is ignored.

    If retry parameter is greater than 0, then task is re-added to the queue if
    download fails. Re-adding decrements the retry and increments the priority.

    `data` are passed to Client.download method as \*\*kwargs.
    """

    def __init__(self, *args, retry=0, **kwargs):
        kwargs['handler'] = self.download
        super().__init__(*args, **kwargs)
        self.retry = retry

    def download(self, client, url, data):
        try:
            client.download(url, **data)
        except requests.RequestException:
            if self.retry > 0:
                logger.warn('%s failed, re-adding', self)
                self.retry -= 1
                self.priority += 1
                return [self]
            raise
