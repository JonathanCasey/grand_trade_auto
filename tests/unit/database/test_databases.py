#!/usr/bin/env python3
"""
Tests the grand_trade_auto.general.databases functionality.

Per [pytest](https://docs.pytest.org/en/reorganize-docs/new-docs/user/naming_conventions.html),
all tiles, classes, and methods will be prefaced with `test_/Test` to comply
with auto-discovery (others may exist, but will not be part of test suite
directly).

Module Attributes:
  N/A

(C) Copyright 2020 Jonathan Casey.  All Rights Reserved Worldwide.
"""
#pylint: disable=protected-access  # Allow for purpose of testing those elements

from grand_trade_auto.database import databases
from grand_trade_auto.database import postgres



def test_get_database(monkeypatch):
    """
    Tests that the `get_database()` method.
    """
    assert databases.get_database('invalid-db-id') is None
    assert databases._dbs_loaded == {}

    assert databases.get_database('postgres-test', 'invalid-env') is None
    assert databases._dbs_loaded == {}

    assert databases.get_database('postgres-test') is not None
    assert databases._dbs_loaded != {}

    databases._dbs_loaded.pop('postgres-test')
    assert databases._dbs_loaded == {}

    assert databases.get_database('postgres-test', 'test') is not None
    assert databases._dbs_loaded != {}

    def mock_get_database_from_config(
            db_id, env=None):                  # pylint: disable=unused-argument
        """
        Replaces the `_get_database_from_config()` so it will find no match.
        """
        return None

    monkeypatch.setattr(databases, '_get_database_from_config',
            mock_get_database_from_config)

    assert databases.get_database('postgres-test') is not None

    assert databases.get_database('postgres-test', 'test') is not None



def test_get_database_from_config(monkeypatch):
    """
    Tests that the `_get_database_from_config()` method.
    """
    assert databases._get_database_from_config('invalid-db-id') is None
    assert databases._get_database_from_config('postgres-test', 'invalid-env') \
            is None
    assert databases._get_database_from_config('postgres-test') is not None
    assert databases._get_database_from_config('postgres-test', 'test') \
            is not None

    def mock_get_type_names():
        """
        Replaces the `get_type_names()` in an database so it will find no match.
        """
        return []

    monkeypatch.setattr(postgres.Postgres, 'get_type_names',
            mock_get_type_names)

    assert databases._get_database_from_config('postgres-test') is None
