# -*- coding: utf-8 -*-
from os import environ as env
import logging
import time

from django.conf import settings
from django.core import mail
from django.core.management import call_command
from django.db import transaction
from django.test import TestCase, Client
from django.urls import clear_url_caches

from .settings import enable_settings_overrides
from .signals import before_test, after_test
from .transactions import noop, disable_transaction_methods, restore_transaction_methods

__all__ = [
    'RollbackTestCase',
]



class RollbackTestCase(TestCase):
    """
    This is a TestCase that will auto-rollback any database changes.
    It also does NOT flush the database.
    Kind of a mix and match from the our current version of django plus the
    latest version that we do not use.
    """
    DEFAULT_SERVER_NAME = 'www.example.com'

    def should_disable_manual_transactions(self):
        return True

    def _pre_setup(self):
        """
        Performs any pre-test setup. This includes:

            * If the Test Case class has a 'fixtures' member, installing the
              named fixtures.
            * If the Test Case class has a 'urls' member, replace the
              ROOT_URLCONF with it.
            * Clearing the mail test outbox.
            * Using transactions for auto-rollback.
            * NOT flushing the database.
            * Disabling setUp for the duration of this test if it is
              being skipped

        """

        enable_settings_overrides()

        logging.debug(f'Starting test: {self}')
        self._start_time = time.time()

        if hasattr(self, 'fixtures') and self.fixtures:
            # We have to use this slightly awkward syntax due to the fact
            # that we're using *args and **kwargs together.
            call_command('loaddata', *self.fixtures, **{'verbosity': 0})

        if hasattr(self, 'urls'):
            settings.overrides['ROOT_URLCONF'] = self.urls
            clear_url_caches()

        mail.outbox = []

        if self.should_disable_manual_transactions():
            # transaction.enter_transaction_management()
            # transaction.managed(True)
            disable_transaction_methods()

        from django.contrib.sites.models import Site
        Site.objects.clear_cache()

        # fixup model_cache prefix in memcache to be make each test run idempotent
        # i.e. to allow row-level cache to accomodate transactional rollbacks
        versions = settings.CACHE_KEY_VERSIONS
        model_cache_version = versions.get('model_cache')
        if model_cache_version:
            versions['model_cache'] = str(time.time())[-6:] # memcache key length limit being hit - so limit to 6

        # Disable the setUp method whenever the test itself is being skipped.

        test_method = getattr(self, self._testMethodName)
        if getattr(test_method, 'SLOW_TEST', False):
            if env.get('SKIP_SLOW_TESTS', False):
                self._skipped_setUp, self.setUp = self.setUp, noop
                self._skipped_tearDown, self.tearDown = self.tearDown, noop

        # Override the default server name.
        self.client = Client(SERVER_NAME=self.DEFAULT_SERVER_NAME)

        before_test.send(self)

    def _post_teardown(self):
        """
        Performs any post-test things. This includes:

            * Putting back the original ROOT_URLCONF if it was changed.
            * Rolling back the database transaction.
            * Restore the setUp if it was skipped.

        """

        after_test.send(self)

        if hasattr(self, 'urls'):
            del settings.overrides['ROOT_URLCONF']
            clear_url_caches()

        if self.should_disable_manual_transactions():
            restore_transaction_methods()
            transaction.rollback()
            # transaction.leave_transaction_management()
            connection.close()

        if hasattr(self, '_skipped_setUp'):
            settings.setUp = self._skipped_setUp
            settings.tearDown = self._skipped_tearDown

        logging.debug('Finished test in %.2fs: %s' % (time.time() - self._start_time, self))

    def __call__(self, result=None):
        """
        Wrapper around default __call__ method to perform timing.
        """

        start_time = time.time()

        super(RollbackTestCase, self).__call__(result)

        if env.get('SHOW_SLOW_TESTS'):
            time_taken = int(time.time() - start_time)
            minutes = time_taken / 60
            seconds = time_taken - (minutes * 60)
            if seconds or minutes:
                print()
                print('Slow Test: %d:%0.2d %s' % (minutes, seconds, self))