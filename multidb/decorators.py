# -*- coding: utf-8 -*-
import functools

from django.forms.utils import ErrorList

from .readonly import read_only_mode, ReadOnlyError
from .signals import send_post_commit, send_post_rollback, send_pre_commit


def full_clean_if_not_read_only(full_clean):
    """Decorator for preventing form submissions while in read-only mode."""

    def wrapper(self):
        full_clean(self)
        if read_only_mode:
            if '__all__' not in self._errors:
                self._errors['__all__'] = ErrorList()
            self._errors.get('__all__').insert(0, ReadOnlyError.message)
            if hasattr(self, 'cleaned_data'):
                delattr(self, 'cleaned_data')

    return wrapper


def wrap(before=None, after=None, condition=lambda *args, **kwargs: True):
    """
    A helper for creating decorators.

    Runs a "before" function before the decorated function, and an "after"
    function afterwards. The condition check is performed once before
    the decorated function.

    """
    def decorator(func):
        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            yes = condition(*args, **kwargs)
            if yes and before:
                before()
            result = func(*args, **kwargs)
            if yes and after:
                after()
            return result
        return wrapped
    return decorator


def wrap_before(before, condition=lambda *args, **kwargs: True):
    """
    A helper for creating decorators.

    Runs a "before" function before the decorated function. The condition
    check is performed before the decorated function is called.

    """
    def decorator(func):
        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            if condition(*args, **kwargs):
                before()
            return func(*args, **kwargs)
        return wrapped
    return decorator


def wrap_after(after, condition=lambda *args, **kwargs: True):
    """
    A helper for creating decorators.

    Runs an "after" function after the decorated function. The condition
    check is performed after the decorated function is called.

    """
    def decorator(func):
        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            result = func(*args, **kwargs)
            if condition(*args, **kwargs):
                after()
            return result
        return wrapped
    return decorator


commit = wrap(
    before=send_pre_commit,
    after=send_post_commit,
)

rollback = wrap_after(
    after=send_post_rollback,
)
