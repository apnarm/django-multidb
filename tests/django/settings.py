# -*- coding: utf-8 -*-
"""
Minimal settings file to satisfy django.setup()
"""
from os import environ as env

SECRET_KEY = '-bogus-'
VERSION = '1'
CACHE_KEY_VERSIONS = {
    'model_cache': VERSION,
    'templates': VERSION,
    'template_cache_blocks': VERSION
}
INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
]