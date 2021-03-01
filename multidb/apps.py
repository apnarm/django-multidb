# -*- coding: utf-8 -*-
from django.apps import AppConfig


class MultiDbAppConfig(AppConfig):
    name = 'multidb'
    verbose_name = 'Multi database with readonly support'

    def ready(self):
        from django.conf import settings
        from django.db import connections
        from django.db.backends.dummy.base import DatabaseWrapper as DummyDatabaseWrapper
        from django.forms.models import BaseModelForm
        from django.db.backends.base.base import BaseDatabaseWrapper

        from . import decorators
        from .connection import ConnectionProxy
        from .cursors import PrintCursorWrapper, RestrictedCursorWrapper

        # Patch Django's form class to handle read-only mode.
        BaseModelForm.full_clean = decorators.full_clean_if_not_read_only(BaseModelForm.full_clean)

        # Patch Django's connection classes (BaseDatabaseWrapper subclasses depending
        # on which engines have been used in settings.DATABASES) to always use
        # the "active" connection that is determined by the middleware.
        for connection_class in set(conn.__class__ for conn in connections.all()):
            if connection_class is not DummyDatabaseWrapper:
                connection_class.__bases__ = (ConnectionProxy,) + connection_class.__bases__

        test_mode = getattr(settings, 'TEST_MODE', False)
        sql_debug = getattr(settings, 'SQL_DEBUG', False)
        sql_query_debug = getattr(settings, 'SQL_QUERY_DEBUG', False)

        # # Patch Django's BaseDatabaseWrapper to enforce database write restrictions.
        # if sql_debug and not test_mode:
        #     def cursor(self):
        #         # DJANGO 1.5: no need for this apparently: makes it break
        #         # cursor = self.make_debug_cursor(self._cursor())
        #         return PrintCursorWrapper(self._cursor(), self)
        # elif sql_query_debug:
        #     def cursor(self):
        #         # DJANGO 1.5: no need for this apparently: makes it break
        #         # cursor = self.make_debug_cursor(self._cursor())
        #         return RestrictedCursorWrapper(cursor, self)
        # else:
        #     def cursor(self):
        #         try:
        #             return RestrictedCursorWrapper(self._cursor(), self)
        #         except Error:
        #             self.close()
        #             return RestrictedCursorWrapper(self._cursor(), self)
        #
        # BaseDatabaseWrapper.cursor = cursor
