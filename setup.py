from setuptools import setup

import os
import re

pkg_name = 'logicoma'

__dir__ = os.path.dirname(__file__)
with open(os.path.join(__dir__, pkg_name, '__init__.py')) as f:
    for line in f:
        if re.match(r'__version__', line):
            exec(line)
            break

setup(
    name=pkg_name,
    version=__version__,
    description='Package for creating simple web crawlers.',
    author='Filip Pobořil',
    author_email='tsuki@fpob.eu',
    license='MIT',
    packages=['logicoma'],
    install_requires=['requests', 'bs4', 'html5lib'],
    entry_points={
        'console_scripts': [
            'logicoma=logicoma.cli:main'
        ],
    },
)
