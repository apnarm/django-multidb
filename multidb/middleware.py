# -*- coding: utf-8 -*-
"""
Middleware for setting the current database according to the current
request's HTTP method.

The databases used will depend on the value of 'HTTP_METHODS' defined in
settings.DATABASES. If more than one database is configured for the same
HTTP method, then this middleware will randomly choose one per-request.

"""

import random

from django.core.exceptions import MiddlewareNotUsed
from django.db import connection, DEFAULT_DB_ALIAS
from django.utils.deprecation import MiddlewareMixin

from . import settings as config
from .connection import connection_state
from .readonly import read_only_mode


class MultiDBMiddleware(MiddlewareMixin):

    def __init__(self, get_response):
        super().__init__(get_response)

        if not config.DATABASE_MAPPINGS and not config.READ_ONLY_DATABASES:
            raise MiddlewareNotUsed

    def get_aliases_for_path(self, path):
        """
        See if the current request path has been configured to use any
        particular databases. This is controlled by defining HTTP_PATHS
        within the settings.DATABASES options.
        """
        db_aliases = []
        for db_alias, paths_regex in config.DATABASE_PATHS.items():
            if paths_regex.search(path):
                db_aliases.append(db_alias)
        return db_aliases

    def get_aliases_for_method(self, method):
        """
        Otherwise, use the request method to determine the database to use.
        This is controlled by defining HTTP_METHODS within the
        settings.DATABASES options, will fallback to any databases that
        have no methods defined and default to "default" if the method has
        not been specified anywhere or where a d.
        """
        return config.DATABASE_MAPPINGS.get(method) or \
               config.DATABASE_MAPPINGS.get(None) or \
               [DEFAULT_DB_ALIAS]

    def override_for_readonly(self, db_aliases):
        """
        Override and use a read-only database when in read-only mode. This is
        controlled by defining READ_ONLY or READ_ONLY_WARNING within the
        settings.DATABASES options. This is slightly more complicated than
        necessary so it can avoid unnecessarily checking the value of
        read_only_mode (which accesses memcache).
        """
        if config.READ_ONLY_DATABASES:
            for alias in db_aliases:
                if alias not in config.READ_ONLY_DATABASES_SET:
                    # One of the options is not a read database,
                    # so read-only mode will have to be checked.
                    if read_only_mode:
                        db_aliases = config.READ_ONLY_DATABASES
                    break
        return db_aliases

    def process_request(self, request):
        db_aliases = self.get_aliases_for_path(request.path)
        if not db_aliases:
            db_aliases = self.override_for_readonly(self.get_aliases_for_method(request.method))

        if len(db_aliases) == 1:
            connection_state.alias = db_aliases[0]
        elif db_aliases:
            connection_state.alias = random.choice(db_aliases)
        else:
            # This request method is not specified in the settings,
            # so use the default database connection.
            connection_state.alias = DEFAULT_DB_ALIAS

    def process_exception(self, request, exception):
        del connection_state.alias

    def process_response(self, request, response):
        del connection_state.alias
        return response



class MultiDBTransactionMiddleware(object):
    """
    Transaction middleware. Optimizes Django's transaction middleware
    to only create transactions when using a writeable database.

    This requires read-only databases to use the "autocommit" option,
    otherwise it will automatically create a transaction as soon as the
    database is accessed.

    """

    def process_request(self, request):
        """
        Enters transaction management, unless the current request
        is using a read-only database.
        """
        if connection.alias in config.READ_ONLY_DATABASES_SET:
            # This is a read-only request, so we know that nothing will be
            # written to the database. There's no need to begin a transaction.
            pass
        else:
            pass
            # Create a transaction.
            # transaction.enter_transaction_management()
            # transaction.managed(True)

    def process_exception(self, request, exception):
        """
        Rolls back the database and leaves transaction management.
        """
        pass
        # if transaction.is_managed():
        #     if transaction.is_dirty():
        #         transaction.rollback()
        #     transaction.leave_transaction_management()

    def process_response(self, request, response):
        """
        Commits and leaves transaction management.
        """
        pass
        # if transaction.is_managed():
        #     if transaction.is_dirty():
        #         transaction.commit()
        #     transaction.leave_transaction_management()

        return response
