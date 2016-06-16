#!/usr/bin/env python
# coding: utf-8

from setuptools import setup
import vctools

setup(
    name='vctools',
    version=vctools.__version__,
    description='A python library to interact with Visual Studio toolchain',
    url='https://github.com/rikdev/PythonVSTools',
    author='Ivan Ryabchenko',
    author_email='rikdev@yandex.com',
    license="MIT",
    classifiers=[
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Topic :: Software Development :: Build Tools",
    ],
    packages=['vctools'],
)
