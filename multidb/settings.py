# -*- coding: utf-8 -*-
from collections import defaultdict
from random import choice
import re

from django.conf import settings
from django.db import DEFAULT_DB_ALIAS

_OPTIONS = 'OPTIONS'
_HTTP_METHODS = 'HTTP_METHODS'
_HTTP_WRITE_PATHS = 'HTTP_WRITE_PATHS'
_READ_ONLY_OPTIONS = ('READ_ONLY', 'READ_ONLY_WARNING')


def _build_mappings():
    """
    Check databases for assigned HTTP methods
    :return: mapping of http methods to eligible databases
    """
    result = defaultdict(list)
    for db_alias, options in settings.DATABASES.items():
        if _HTTP_METHODS not in options:
            options = options.get(_OPTIONS, [])
        if _HTTP_METHODS not in options:
            # master/writable unrestricted by method
            result[None].append(db_alias)
        else:
            for http_method in options.get(_HTTP_METHODS, []):
                result[http_method].append(db_alias)
    return result


def _get_read_only_databases():
    result = set()
    for db_alias, options in settings.DATABASES.items():
        for read_only_option in _READ_ONLY_OPTIONS:
            if read_only_option not in options:
                options = options.get(_OPTIONS, [])
            if options.get(read_only_option):
                result.add(db_alias)
                break
    return result


def _build_paths():
    """
    Built list of paths that should always use the master/write
    database, even for read requests
    :return: mapping of urls/paths for each database
    """
    result = {}
    for db_alias, options in settings.DATABASES.items():
        paths = options.get(_HTTP_WRITE_PATHS)
        if paths:
            any_path = '|'.join(re.escape(path) for path in paths)
            regex = re.compile(r'^(%s)' % any_path)
            result[db_alias] = regex
    return result


# Determine the HTTP method to database alias mappings.
# It will be in the format
# {
#   http_method1: [alias?, alias?, ...],
#   http_method2: [alias?, alias?, ...],
#   ...
# }
DATABASE_MAPPINGS = _build_mappings()


# Determine a single fallback database to use.
# This persists for the entire life of the process, so it can be relied upon.
FALLBACK_DATABASE = choice(DATABASE_MAPPINGS.get(None) or [DEFAULT_DB_ALIAS])


# Determine which paths should be excluded from each database.
# For example, the /admin/ URLs should not be read-only.
# It will be in the format
# {
#   alias1: '^(pathx1|pathx2|...|pathxN)'
#   alias2: '^(pathy1|pathy2|...|pathyN)'
#   ...
# }
DATABASE_PATHS = _build_paths()


# Determine which databases are for read-only purposes.
READ_ONLY_DATABASES_SET = _get_read_only_databases()
READ_ONLY_DATABASES = list(READ_ONLY_DATABASES_SET)
