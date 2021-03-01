# -*- coding: utf-8 -*-
from django.db import connection, transaction


__all__ = [
    'noop',
    'disable_transaction_methods',
    'restore_transaction_methods',
]


real_commit = transaction.commit
real_rollback = transaction.rollback
real_savepoint_commit = transaction.savepoint_commit
real_savepoint_rollback = transaction.savepoint_rollback
real_connection_close = connection.close
# real_managed = transaction.managed
# real_enter_transaction_management = transaction.enter_transaction_management
# real_leave_transaction_management = transaction.leave_transaction_management


def noop(*_args, **_kwargs):
    return


def disable_transaction_methods():
    transaction.commit = noop
    transaction.rollback = noop
    transaction.savepoint_commit = noop
    transaction.savepoint_rollback = noop
    transaction.enter_transaction_management = noop
    transaction.leave_transaction_management = noop
    transaction.managed = noop
    connection.close = noop


def restore_transaction_methods():
    transaction.commit = real_commit
    transaction.rollback = real_rollback
    transaction.savepoint_commit = real_savepoint_commit
    transaction.savepoint_rollback = real_savepoint_rollback
    connection.close = real_connection_close
    # transaction.enter_transaction_management = real_enter_transaction_management
    # transaction.leave_transaction_management = real_leave_transaction_management
    # transaction.managed = real_managed
