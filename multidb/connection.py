# -*- coding: utf-8 -*-
import contextlib
import threading

from django.db import connections

from .settings import FALLBACK_DATABASE


class ConnectionState(threading.local):

    _alias = FALLBACK_DATABASE

    def _get_alias(self):
        return self._alias

    def _set_alias(self, value):
        self._alias = value

    def _del_alias(self):
        self._alias = FALLBACK_DATABASE

    alias = property(_get_alias, _set_alias, _del_alias)

    @contextlib.contextmanager
    def force(self, value):
        old_value = self.alias
        self.alias = value
        try:
            yield
        finally:
            self.alias = old_value


class ConnectionProxy(object):

    def __init__(self, *args, **kwargs):
        with connection_state.force(None):
            super(ConnectionProxy, self).__init__(*args, **kwargs)

    def __getattribute__(self, name):
        alias = connection_state.alias
        # This is supporting Django 1.2 / 1.4 where in 1.2 _connections is a dict and in 1.4 it's threads.local()
        # - if there's an alias then the connection has already been initialized, otherwise use self.
        if alias and (
            isinstance(connections._connections, dict) and alias in connections._connections or
            alias in connections._connections.__dict__
        ):
            connection = alias and connections[alias] or self
        else:
            connection = self

        return super(ConnectionProxy, connection).__getattribute__(name)

    def __setattr__(self, name, value):
        alias = connection_state.alias
        # This is supporting Django 1.2 / 1.4 where in 1.2 _connections is a dict and in 1.4 it's threads.local()
        # - if there's an alias then the connection has already been initialized, otherwise use self.
        if alias and (
            isinstance(connections._connections, dict) and alias in connections._connections or
            alias in connections._connections.__dict__
        ):
            connection = alias and connections[alias] or self
        else:
            connection = self

        return super(ConnectionProxy, connection).__setattr__(name, value)

    @property
    def is_mysql(self):
        if not hasattr(self, '_is_mysql'):
            self._is_mysql = 'mysql' in self.settings_dict['ENGINE']
        return self._is_mysql

    @property
    def is_postgresql(self):
        if not hasattr(self, '_is_postgresql'):
            self._is_postgresql = 'postgresql' in self.settings_dict['ENGINE']
        return self._is_postgresql


connection_state = ConnectionState()
