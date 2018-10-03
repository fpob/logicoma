.. Logicoma documentation master file, created by
   sphinx-quickstart on Tue Oct  2 22:52:14 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Logicoma's documentation!
====================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:
   :glob:

   *

Logicoma is Python package for creating simple web crawlers with as little code
as necessary. It aims to make simple web crawlers as quick as possible.

If some complex crawling is needed, this package may not be the right choice,
`Scrapy <https://scrapy.org/>`_ or something else could be better choice.


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
