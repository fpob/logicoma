from setuptools import setup
from os import path
import re


__dir__ = path.dirname(__file__)


with open(path.join(__dir__, 'logicoma', '__init__.py')) as f:
    for line in f:
        if re.match(r'__version__', line):
            exec(line)
            break

with open(path.join(__dir__, 'README.rst')) as f:
    long_description = f.read()


setup(
    name='logicoma',
    version=__version__,
    description='Package for creating simple web crawlers.',
    long_description=long_description,
    author='Filip Pobořil',
    author_email='tsuki@fpob.eu',
    url='https://github.com/fpob/logicoma',
    download_url='https://github.com/fpob/logicoma/archive/v{}.tar.gz'.format(__version__),
    license='MIT',
    keywords=['Web Crawling'],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Internet :: WWW/HTTP',
    ],
    packages=['logicoma'],
    install_requires=['requests', 'bs4', 'html5lib', 'click']
)
