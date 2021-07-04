#!/usr/bin/env python3
"""
Tests the grand_trade_auto.database.database_meta functionality.

Per [pytest](https://docs.pytest.org/en/reorganize-docs/new-docs/user/naming_conventions.html),
all tiles, classes, and methods will be prefaced with `test_/Test` to comply
with auto-discovery (others may exist, but will not be part of test suite
directly).

Module Attributes:
  N/A

(C) Copyright 2021 Jonathan Casey.  All Rights Reserved Worldwide.
"""
import logging

from grand_trade_auto.database import database_meta
from grand_trade_auto.database import postgres



def test_database_init(caplog):
    """
    Tests the `__init__()` method of `Database`, at least for its unique
    functionality that is not expected to be tested anywhere else.
    """

    class MockDatabaseChild(database_meta.Database):
        """"
        Simple mock object to subclass Database.
        """

        @classmethod
        def load_from_config(cls, db_cp, db_id, secrets_id):
            """
            Not needed / will not be used.
            """
            return

        @classmethod
        def get_dbms_names(cls):
            """
            Not needed / will not be used.
            """
            return

        def create_db(self):
            """
            Not needed / will not be used.
            """
            return

    caplog.set_level(logging.WARNING)
    caplog.clear()
    MockDatabaseChild('mock_env', 'mock_cp_db_id', 'mock_cp_secrets_id')
    assert caplog.record_tuples == []

    extra_kwargs = {
            'key1': 'val1',
            'key2': 'val2',
    }
    caplog.clear()
    MockDatabaseChild('mock_env', 'mock_cp_db_id', 'mock_cp_secrets_id',
            **extra_kwargs)
    assert caplog.record_tuples == [
            ('grand_trade_auto.database.database_meta', logging.WARNING,
                'Discarded excess kwargs provided to MockDatabaseChild:'
                + ' key1, key2')
    ]

    # Using Postgres to test inheritance consumption
    kwargs = {
        'env': 'mock_env',
        'cp_db_id': 'mock_cp_db_id',
        'cp_secrets_id': 'mock_cp_secrets_id',
        **extra_kwargs,
    }
    caplog.clear()
    postgres.Postgres('mock_host', -1, 'mock_database', **kwargs)
    assert caplog.record_tuples == [
            ('grand_trade_auto.database.database_meta', logging.WARNING,
                'Discarded excess kwargs provided to Postgres: key1, key2')
    ]



def test_matches_id_criteria():
    """
    Tests the `matches_id_criteria()` method of `Database`.
    """

    class MockDatabaseChild(database_meta.Database):
        """"
        Simple mock object to subclass database.
        """

        @classmethod
        def load_from_config(cls, db_cp, db_id, secrets_id):
            """
            Not needed / will not be used.
            """
            return

        @classmethod
        def get_dbms_names(cls):
            """
            Need at least 1 name to match.
            """
            return ['mock_dbms']

        def create_db(self):
            """
            Not needed / will not be used.
            """
            return

    db = MockDatabaseChild('mock_env', 'mock_cp_db_id', 'mock_cp_secrets_id')
    assert not db.matches_id_criteria('invalid-db-id')
    assert db.matches_id_criteria('mock_cp_db_id')
    assert not db.matches_id_criteria('mock_cp_db_id', 'invalid-env')
    assert db.matches_id_criteria('mock_cp_db_id', 'mock_env')
    assert not db.matches_id_criteria('mock_cp_db_id', dbms='invalid-dbms')
    assert db.matches_id_criteria('mock_cp_db_id', dbms='mock_dbms')
    assert not db.matches_id_criteria('mock_cp_db_id', 'invalid-env',
            'mock_dbms')
    assert not db.matches_id_criteria('mock_cp_db_id', 'mock_env',
            'invalid-dbms')
    assert db.matches_id_criteria('mock_cp_db_id', 'mock_env', 'mock_dbms')
