#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from distutils.core import setup

setup(
    name='django-multidb',
    version='0.1.0',
    description='Read/write database splitting for Django, based on the HTTP request method',
    author='Raymond Butcher',
    author_email='randomy@gmail.com',
    url='https://github.com/apnarm/django-multidb',
    license='MIT',
    packages=[
        'multidb'
    ],
    install_requires=[
        'django',
        'psycopg2-binary',
    ]
)
