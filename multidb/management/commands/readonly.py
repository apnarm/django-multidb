# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from django.utils.translation import gettext as _

from ...readonly import read_only_mode


class Command(BaseCommand):

    help = _('Manage the read-only status of the database.')

    requires_migration_checks = False

    def add_arguments(self, parser):
        parser.add_argument('action', action='store', choices=('enable', 'disable', 'status'),
                            help=_('Action to take'))

    def handle(self, action=None, **options):
        outfp = self.stdout

        methods = {
            'enable': self.enable,
            'disable': self.disable,
            'status': self.status,
        }
        try:
            method = methods[action]
        except KeyError:
            raise CommandError(f"unknown action '{action}'")
        else:
            method()

    def enable(self):
        read_only_mode.enable()
        self.status()

    def disable(self):
        read_only_mode.disable()
        self.status()

    def status(self):
        if read_only_mode:
            print('Server is in read-only mode')
        else:
            print('Server is in read/write mode')
