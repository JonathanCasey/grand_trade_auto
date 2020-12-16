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
# pylint: disable=redefined-outer-name  # Otherwise fixtures produce warning
import psycopg2
import pytest

from grand_trade_auto.database import database_postgres
from grand_trade_auto.database import databases



@pytest.fixture
def pg_test_db():
    """
    Gets the test database handle for postgres.

    Returns:
      (DatabasePostgres): The test postgres database handle.
    """
    return databases.get_database_from_config('test', 'postgres')



def test_load_from_config(pg_test_db):
    """
    Tests the `load_from_config()` method in `DatabasePostgres`.

    TODO: This should load its own conf files and test directly; but good enough
    for now.
    """
    assert pg_test_db is not None



def test_get_type_names():
    """
    Tests the `get_type_names()` method in `DatabasePostgres`.  Not an
    exhaustive test.
    """
    assert 'postgres' in database_postgres.DatabasePostgres.get_type_names()
    assert 'not-postgres' not in \
            database_postgres.DatabasePostgres.get_type_names()



def test_connect(pg_test_db):
    """
    Tests the `connect()` method in `DatabasePostgres`.  Only tests connecting
    to the default database; connecting to the real test db will be covered by
    another test.
    """
    conn = pg_test_db.connect('postgres')
    assert conn is not None

    pg_test_db.database = 'invalid-database'
    with pytest.raises(psycopg2.OperationalError):
        conn = pg_test_db.connect()



def test_get_conn(pg_test_db):
    """
    Tests the `get_conn()` method in `DatabasePostgres`.
    """
    pg_test_db.conn = 'test-conn'
    conn = pg_test_db.get_conn()
    assert conn == 'test-conn'
