# -*- coding: utf-8 -*-
from django.core.signals import Signal

__all__ = [
    'before_test',
    'after_test',
]

before_test = Signal()
after_test = Signal()
