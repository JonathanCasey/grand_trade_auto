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



@pytest.mark.alters_db_schema
@pytest.mark.order(0)
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



def test_cursor(pg_test_db):
    """
    Tests the `cursor()` method in `Postgres`.
    """
    conn_2 = pg_test_db.connect(False)

    assert pg_test_db._conn is None
    cursor = pg_test_db.cursor()
    assert pg_test_db._conn is not None
    assert cursor.connection == pg_test_db._conn
    assert cursor.name is None
    cursor.close()

    cursor = pg_test_db.cursor(conn=conn_2)
    assert pg_test_db._conn is not None
    assert pg_test_db._conn != conn_2
    assert cursor.connection == conn_2
    assert cursor.name is None
    cursor.close()

    test_cursor_name = 'test_cursor'
    cursor = pg_test_db.cursor(test_cursor_name)
    assert cursor.connection == pg_test_db._conn
    assert cursor.name == test_cursor_name
    cursor.close()

    cursor = pg_test_db.cursor(conn=conn_2, cursor_name=test_cursor_name,
            extra_arg='extra_val_1')
    assert cursor.connection == conn_2
    assert cursor.name == test_cursor_name
    cursor.close()

    pg_test_db._conn.close()
    conn_2.close()



def test_execute(pg_test_db):               #pylint: disable=too-many-statements
    """
    Tests the `execute()` method in `Postgres`.

    While this does alter DB schema, it does it only for its own isolated
    purposes that won't conflict with other tests, so does not need to be
    marked as alters_db_schema.
    """
    # Test with cached connection to test database
    pg_test_db.connect()

    test_table_name = 'test_postgres__test_execute'

    def _drop_test_table():
        """
        Drops the test table for this test.
        """
        sql_drop_table = f'DROP TABLE IF EXISTS {test_table_name}'
        cursor = pg_test_db.connect().cursor()
        cursor.execute(sql_drop_table)
        pg_test_db.connect().commit()
        cursor.close()

    # Ensure test table does not exist
    _drop_test_table()

    # Want to test parameter-less command works
    sql_create_table = f'''
        CREATE TABLE {test_table_name} (
        id serial PRIMARY KEY,
        test_col_a integer,
        test_col_b text
    )
    '''
    cursor = pg_test_db.execute(sql_create_table)
    assert cursor.connection == pg_test_db._conn
    assert cursor.name is None
    assert cursor.closed is True

    # Want to test that normal insertion works
    sql_insert_data = f'''
        INSERT INTO {test_table_name}
        (test_col_a, test_col_b)
        VALUES (%(test_val_a)s, %(test_val_b)s)
    '''
    test_vals_1 = {
        'test_val_a': 1,
        'test_val_b': 'one',
    }
    cursor = pg_test_db.execute(sql_insert_data, val_vars=test_vals_1)
    assert cursor.connection == pg_test_db._conn
    assert cursor.name is None
    assert cursor.closed is True

    # Want to test select and named cursors without commit and close works
    sql_select_where_data = f'''
        SELECT test_col_b
        FROM {test_table_name}
        WHERE test_col_a=%(test_val_a)s
    '''
    test_cursor_name = 'test_execute'
    cursor = pg_test_db.execute(sql_select_where_data, val_vars=test_vals_1,
            cursor_name=test_cursor_name, commit=False, close_cursor=False)
    assert cursor.connection == pg_test_db._conn
    assert cursor.name == test_cursor_name
    assert cursor.closed is False
    # assert cursor.rowcount == 1
    assert cursor.fetchone()[0] == test_vals_1['test_val_b']
    cursor.close()

    # Want to test that not committing an insertion truly does not commit...
    test_vals_2 = {
        'test_val_a': 2,
        'test_val_b': 'two',
    }
    cursor = pg_test_db.execute(sql_insert_data, val_vars=test_vals_2,
            commit=False)
    assert cursor.connection == pg_test_db._conn
    assert cursor.name is None
    assert cursor.closed is True
    cursor.close()

    # ...by verifying does not show up on a select, while also trying a 2nd conn
    sql_select_data = f'''
        SELECT test_col_b
        FROM {test_table_name}
        ORDER BY id
    '''
    conn_2 = pg_test_db.connect(False)
    assert conn_2 != pg_test_db._conn
    cursor = pg_test_db.execute(sql_select_data, val_vars=test_vals_1,
            close_cursor=False, conn=conn_2)
    assert cursor.connection == conn_2
    assert cursor.name is None
    assert cursor.closed is False
    assert cursor.rowcount == 1
    assert cursor.fetchone()[0] == test_vals_1['test_val_b']
    cursor.close()

    # ...but committing 1st conn does show 2nd row, while also providing cursor
    # (and conn arg ignored if cursor provided)
    pg_test_db._conn.commit()
    cursor = pg_test_db.cursor()
    cursor_2 = pg_test_db.execute(sql_select_data, val_vars=test_vals_1,
            close_cursor=False, cursor=cursor, conn=conn_2)
    assert cursor_2 == cursor
    assert cursor.connection == pg_test_db._conn
    assert pg_test_db._conn != conn_2
    assert cursor.name is None
    assert cursor.closed is False
    assert cursor.rowcount == 2
    assert cursor.fetchone()[0] == test_vals_1['test_val_b']
    assert cursor.fetchone()[0] == test_vals_2['test_val_b']
    cursor.close()

    # Ensure cleaned up for this test
    conn_2.close()
    _drop_test_table()
    pg_test_db._conn.close()
