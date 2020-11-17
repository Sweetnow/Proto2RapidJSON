#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='proto2rapidjson',
    version='1.0.0',
    packages=find_packages(),
    python_requires=">=3.6",
    description='Convert .proto file to header-only RapidJSON based c++ code',
    author='Jun Zhang',
    author_email='zhangjun990222@gmail.com',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Sweetnow/proto2rapidjson",
    entry_points={
        'console_scripts': [
            'command-name = proto2rapidjson.__main__:entry',
        ],
    },
    zip_safe=False
)
