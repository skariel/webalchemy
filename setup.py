#!/usr/bin/env python

from setuptools import setup, find_packages
from glob import glob

def readme():
    return '''Check the homepage for details'''

exec(open('webalchemy/version.py').read())
setup(
    name='Webalchemy',
    version=__version__,
    description='Modern web development with Python',
    long_description=readme(),
    keywords='web development, websocket',
    package_dir={'webalchemy': 'webalchemy'},
    package_data={
        'webalchemy':['webalchemy/*'],
        'webalchemy/js':['webalchemy/js/*']
    },
    classifiers=[
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    url='https://github.com/skariel/webalchemy',
    author="Jose Ariel Keselman",
    author_email='skariel@gmail.com',
    install_requires=[
        'docopt==0.6.1',
        'pythonium==0.6.2',
        'sockjs-tornado==1.0.0',
        'tornado==3.2',
        'beautifulsoup4==4.3.2'
    ],
    license="MIT",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
)

