#!/usr/bin/env python3
"""
Tests the grand_trade_auto.general.database_postgres functionality.

Per [pytest](https://docs.pytest.org/en/reorganize-docs/new-docs/user/naming_conventions.html),
all tiles, classes, and methods will be prefaced with `test_/Test` to comply
with auto-discovery (others may exist, but will not be part of test suite
directly).

Module Attributes:
  N/A

(C) Copyright 2020 Jonathan Casey.  All Rights Reserved Worldwide.
"""
import psycopg2
import pytest

from grand_trade_auto.database import database_postgres
from grand_trade_auto.database import databases



def test_load_from_config():
    """
    Tests the `load_from_config()` method in `DatabasePostgres`.

    TODO: This should load its own conf files and test directly; but good enough
    for now.
    """
    db_handle = databases.get_database_from_config('test', 'postgres')
    assert db_handle is not None



def test_get_type_names():
    """
    Tests the `get_type_names()` method in `DatabasePostgres`.  Not an
    exhaustive test.
    """
    assert 'postgres' in database_postgres.DatabasePostgres.get_type_names()
    assert 'not-postgres' not in \
            database_postgres.DatabasePostgres.get_type_names()



def test_connect():
    """
    Tests the `connect()` method in `DatabasePostgres`.  Only tests connecting
    to the default database; connecting to the real test db will be covered by
    another test.
    """
    db_handle = databases.get_database_from_config('test', 'postgres')
    conn = db_handle.connect('postgres')
    assert conn is not None

    db_handle.database = 'invalid-database'
    with pytest.raises(psycopg2.OperationalError):
        conn = db_handle.connect()
