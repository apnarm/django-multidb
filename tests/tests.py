# -*- coding: utf-8 -*-
from os import environ as env
from django.contrib.contenttypes.models import ContentType
from django.forms.models import modelform_factory

from multidb.readonly import read_only_mode, ReadOnlyError
from testuils.rollback import RollbackTestCase

env['DJANGO_SETTINGS_MODULE'] = 'django.settings'


class ReadOnlyTestCase(RollbackTestCase):
    """
    These tests only work if caching is enabled.
    No big deal if they aren't run every time.

    """

    def setUp(self):
        """
        Record the current state of read-only mode and then ensure that it
        is enabled. The test cases will only run if enabling it was successful.
        If it was not enabled successfully, then it is most likely because
        the project's cache backend is not configured or working.

        """

        self.read_only_was_disabled = not read_only_mode
        if not read_only_mode:
            read_only_mode.enable()

    def tearDown(self):
        """Revert the read-only state."""
        if self.read_only_was_disabled:
            read_only_mode.disable()

    def test_save(self):

        if not read_only_mode:
            return

        try:
            ContentType.objects.all()[0].save()
            self.fail('ReadOnlyError was not raised, it should have been.')
        except ReadOnlyError:
            pass

    def test_modelform(self):

        if not read_only_mode:
            return

        # Create a bound form.
        ContentTypeForm = modelform_factory(ContentType, fields=[])
        form = ContentTypeForm(data={})

        # It should have errors because it's empty, and be invalid.
        self.assertFalse(form.is_valid())

        # The read-only error message should have been added to the form.
        self.assertTrue(ReadOnlyError.message in form._errors.get('__all__', {}))
