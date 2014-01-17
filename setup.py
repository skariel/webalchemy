#!/usr/bin/env python

from setuptools import setup


def readme():
    with open('README.md') as f:
        return f.read()


def version():
    with open('VERSION') as f:
        return f.read()

setup(
    name='Webalchemy',
    version=version(),
    description='Modern web development with Python',
    long_description=readme(),
    keywords='web development, websocket',
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
        "tornado>=3.2",
        "pythonium>=0.6.2"
    ],
    license="MIT",
    packages=['webalchemy'],
    include_package_data=True,
    zip_safe=False,
)
