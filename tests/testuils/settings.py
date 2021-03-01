# -*- coding: utf-8 -*-
import logging

from django.conf import LazySettings, settings

__all__ = [
    'enable_settings_overrides',
    'has_setting',
    'setting_contains',
]


def enable_settings_overrides(clear=True):
    """
    Enable overrides for Django settings. This is used by the unittest code
    to override the ROOT_URLCONF setting. That setting is handled specially by
    the settings facade, so we cannot simply override the value. This has been
    done as a separate additional "settings facade" decorator so that we don't
    have any extra processing when serving requests on production.
    Usage:
        enable_settings_overrides()
        from django.conf import settings
        settings.overrides['ROOT_URLCONF'] = 'bd.urls'
    """

    if hasattr(LazySettings, 'overrides'):
        if clear:
            LazySettings.overrides.clear()
        return

    LazySettings.overrides = {}

    def settings_overrides(func):
        def wrapper(self, name):
            if name in LazySettings.overrides:
                return LazySettings.overrides[name]
            else:
                return func(self, name)
        return wrapper

    LazySettings.__getattr__ = settings_overrides(LazySettings.__getattr__)


def has_setting(variable):
    """
    A decorator that will execute a unit test if the setting is on.
    """

    def wrap(func):

        def wrapped_func(*args, **kwargs):

            if getattr(settings, variable, False):
                func(*args, **kwargs)
            else:
                logging.debug("Skipping test: %s. %s condition not met" % (func.__name__, variable))
                return

        return wrapped_func

    return wrap


def setting_contains(variable, value):
    """
    A decorator that will execute a unit test if the setting is on and contains a value
    """

    def wrap(func):

        def wrapped_func(*args, **kwargs):

            iterable = getattr(settings, variable, False)
            if iterable and value in iterable:
                func(*args, **kwargs)
            else:
                logging.debug("Skipping test: {func.__name__}. {variable} does not contain {value}")
                return

        return wrapped_func

    return wrap
