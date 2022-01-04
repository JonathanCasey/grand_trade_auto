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
#pylint: disable=protected-access  # Allow for purpose of testing those elements

import logging

import pytest

from grand_trade_auto.database import database_meta
from grand_trade_auto.database import postgres



class MockDatabaseChild(database_meta.Database):
    """"
    Simple mock class to subclass Database.
    """

    @classmethod
    def load_from_config(cls, db_cp, db_id):
        """
        Not needed / will not be used.
        """
        return

    @classmethod
    def get_dbms_names(cls):
        """
        Need at least 1 name to match in some tests.
        """
        return ['mock_dbms']

    def create_db(self):
        """
        Not needed / will not be used.
        """
        return

    def cursor(self, cursor_name=None, **kwargs):
        """
        Not needed / will not be used.
        """
        return

    def execute(self, command, val_vars=None, cursor=None, commit=True,
            close_cursor=True):
        """
        Not needed / will not be used.
        """
        return



def test_database_init(caplog):
    """
    Tests the `__init__()` method of `Database`, at least for its unique
    functionality that is not expected to be tested anywhere else.
    """
    caplog.set_level(logging.WARNING)
    caplog.clear()
    MockDatabaseChild('mock_env', 'mock_db_id')
    assert caplog.record_tuples == []

    extra_kwargs = {
            'key1': 'val1',
            'key2': 'val2',
    }
    caplog.clear()
    MockDatabaseChild('mock_env', 'mock_db_id', **extra_kwargs)
    assert caplog.record_tuples == [
            ('grand_trade_auto.database.database_meta', logging.WARNING,
                'Discarded excess kwargs provided to MockDatabaseChild:'
                + ' key1, key2')
    ]

    # Using Postgres to test inheritance consumption
    kwargs = {
        'env': 'mock_env',
        'db_id': 'mock_db_id',
        **extra_kwargs,
    }
    caplog.clear()
    postgres.Postgres('mock_host', -1, 'mock_database', 'mock_user',
            'mock_password', **kwargs)
    assert caplog.record_tuples == [
            ('grand_trade_auto.database.database_meta', logging.WARNING,
                'Discarded excess kwargs provided to Postgres: key1, key2')
    ]



def test_orm():
    """
    Tests the `orm` @property of `Database`.
    """
    db = MockDatabaseChild('mock_env', 'mock_db_id')
    assert db.orm is None
    db._orm = 'test orm'
    assert db.orm == 'test orm'
    with pytest.raises(AttributeError) as ex:
        db.orm = 'unsettable test orm'
    assert "can't set attribute" in str(ex.value)



def test_matches_id_criteria():
    """
    Tests the `matches_id_criteria()` method of `Database`.
    """
    db = MockDatabaseChild('mock_env', 'mock_db_id')
    assert not db.matches_id_criteria('invalid-db-id')
    assert db.matches_id_criteria('mock_db_id')
    assert not db.matches_id_criteria('mock_db_id', 'invalid-env')
    assert db.matches_id_criteria('mock_db_id', 'mock_env')
    assert not db.matches_id_criteria('mock_db_id', dbms='invalid-dbms')
    assert db.matches_id_criteria('mock_db_id', dbms='mock_dbms')
    assert not db.matches_id_criteria('mock_db_id', 'invalid-env', 'mock_dbms')
    assert not db.matches_id_criteria('mock_db_id', 'mock_env', 'invalid-dbms')
    assert db.matches_id_criteria('mock_db_id', 'mock_env', 'mock_dbms')



def test_connect():
    """
    Tests the `connect()` method of `Database`.
    """
    db = MockDatabaseChild('mock_env', 'mock_db_id')
    assert db.connect() is None
    assert db.connect(False, 'mock db name') is None
    assert db.connect(cache=False, database='mock db name') is None
