from setuptools import setup

import logicoma


setup(
    name='logicoma',
    version=logicoma.__version__,
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
