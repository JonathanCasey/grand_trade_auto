#!/usr/bin/env python3
"""
Tests the grand_trade_auto.general.postgres functionality.

Per [pytest](https://docs.pytest.org/en/reorganize-docs/new-docs/user/naming_conventions.html),
all tiles, classes, and methods will be prefaced with `test_/Test` to comply
with auto-discovery (others may exist, but will not be part of test suite
directly).

Module Attributes:
  N/A

(C) Copyright 2020 Jonathan Casey.  All Rights Reserved Worldwide.
"""
#pylint: disable=protected-access  # Allow for purpose of testing those elements

import psycopg2
import pytest

from grand_trade_auto.database import postgres
from grand_trade_auto.database import databases



@pytest.fixture(name='pg_test_db')
def fixture_pg_test_db():
    """
    Gets the test database handle for postgres.

    Returns:
      (Postgres): The test postgres database handle.
    """
    # This also ensures its support was added to databases.py
    return databases._get_database_from_config('postgres-test', 'test')



def test_postgres_init():
    """
    Tests the `__init__()` method in `Postgres`.
    """
    params = {
        'env': 'test',
        'db_id': 'test_db_id',
        'host': 'test_host',
        'port': 0,
        'database': 'test_database',
        'user': 'test_user',
        'password': 'test_password',
    }
    pg_test = postgres.Postgres(**params)
    for k, v in params.items():
        assert pg_test.__getattribute__(f'_{k}') == v
    assert pg_test._conn is None
    assert pg_test._orm._db == pg_test



def test_load_from_config(pg_test_db):
    """
    Tests the `load_from_config()` method in `Postgres`.

    TODO: This should load its own conf files and test directly; but good enough
    for now.
    """
    assert pg_test_db is not None



def test_get_dbms_names():
    """
    Tests the `get_dbms_names()` method in `Postgres`.  Not an exhaustive test.
    """
    assert 'postgres' in postgres.Postgres.get_dbms_names()
    assert 'not-postgres' not in postgres.Postgres.get_dbms_names()



def test_connect(pg_test_db):
    """
    Tests the `connect()` method in `Postgres`.  Only tests connecting to the
    default database; connecting to the real test db will be covered by another
    test.
    """
    conn = pg_test_db.connect(cache=False, database='postgres')
    assert conn is not None

    pg_test_db._database = 'invalid-database'
    with pytest.raises(psycopg2.OperationalError):
        conn = pg_test_db.connect()

    pg_test_db._conn = 'test-conn'
    assert pg_test_db.connect() == 'test-conn'
    assert pg_test_db._conn == 'test-conn'



def test_create_drop_check_if_db_exists(pg_test_db):
    """
    Tests the `create_db()`, `_drop_db()`, and `_check_if_db_exists()` methods
    in `Postgres`.  Done together since they are already intertwined and test
    steps end up being very similar unless duplicating a bunch of code.
    """
    # Want to ensure db does not exist before starting
    pg_test_db._drop_db()
    assert not pg_test_db._check_if_db_exists()

    # Test with cached connection to start
    pg_test_db.connect(True, 'postgres')

    pg_test_db.create_db()
    assert pg_test_db._check_if_db_exists()

    # Re-check the non-create path
    pg_test_db.create_db()
    assert pg_test_db._check_if_db_exists()

    # Need to ensure it definitely is dropped when known to exist
    pg_test_db._drop_db()
    assert not pg_test_db._check_if_db_exists()

    pg_test_db._conn.close()
    # Retest without open cached conn

    pg_test_db.create_db()
    assert pg_test_db._check_if_db_exists()

    pg_test_db._drop_db()
    assert not pg_test_db._check_if_db_exists()



def test__get_conn(pg_test_db):
    """
    Tests the `_get_conn()` method in `Postgres`.
    """
    cached_conn = 'cached conn'
    other_conn = 'other conn'
    extra_args = {
        'extra_arg_1': 'extra_val_1',
        'extra_arg_2': 'extra_val_2',
    }

    assert pg_test_db._conn is None
    assert pg_test_db._get_conn(other_conn) == other_conn

    pg_test_db._conn = cached_conn
    assert pg_test_db._get_conn() == cached_conn
    assert pg_test_db._get_conn(other_conn) == other_conn
    assert pg_test_db._get_conn(**extra_args) == cached_conn
    assert pg_test_db._get_conn(other_conn, **extra_args) == other_conn
