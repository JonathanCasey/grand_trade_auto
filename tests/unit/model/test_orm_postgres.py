#!/usr/bin/env python3
"""
Tests the grand_trade_auto.model.orm_postgres functionality.

Per [pytest](https://docs.pytest.org/en/reorganize-docs/new-docs/user/naming_conventions.html),
all tiles, classes, and methods will be prefaced with `test_/Test` to comply
with auto-discovery (others may exist, but will not be part of test suite
directly).

Module Attributes:
  N/A

(C) Copyright 2021 Jonathan Casey.  All Rights Reserved Worldwide.
"""
#pylint: disable=protected-access  # Allow for purpose of testing those elements

import pytest



@pytest.fixture(name='pg_test_orm')
def fixture_pg_test_orm(pg_test_db):
    """
    Gets the test Orm handle for Postgres.

    Returns:
      (PostgresOrm): The test Postgres Orm object.
    """
    # This also tests init works and Postgres is properly integrated
    return pg_test_db._orm



def _test_create_schema(orm, test_func, table_name, table_schema='public'):
    """
    A generic set of steps to test table creation.

    This will alter the database schema for the database in the provided orm,
    ultimately leaving the table non-existent, so tests using this likely should
    be marked with alters_db_schema.

    This will use the cached connection of the Orm's db, so the caller must
    handle closing that connection.

    Args:
      orm (PostgresOrm): The PostgresOrm to use for this test.
      test_func (function): The create schema function to test, probably from
        that Orm.
      table_name (str): The name of the table that is being created.
      table_schema (str): The schema name of the table that is being created.
        Can likely use default unless it was changed elsewhere.
    """
    def _drop_own_table():
        """
        Drop the table being created in this subtest.
        """
        sql_drop_table = f'DROP TABLE IF EXISTS {table_name}'
        cursor = orm._db.connect().cursor()
        cursor.execute(sql_drop_table)
        cursor.connection.commit()
        cursor.close()

    _drop_own_table()

    # Sanity check -- ensure table really does not exist
    sql_table_exists = f'''
        SELECT EXISTS (
        SELECT FROM information_schema.tables
        WHERE  table_schema = '{table_schema}'
        AND    table_name   = '{table_name}'
    )
    '''

    cursor = orm._db.execute(sql_table_exists, close_cursor=False)
    assert cursor.fetchone()[0] is False
    cursor.close()

    test_func()
    cursor = orm._db.execute(sql_table_exists, close_cursor=False)
    assert cursor.fetchone()[0] is True
    cursor.close()

    _drop_own_table()



@pytest.mark.alters_db_schema
@pytest.mark.order(1)
def test__create_schema_datafeed_src(pg_test_orm):
    """
    Tests the `_create_schema_datafeed_src()` method in `PostgresOrm`.
    """
    # Ensure db exists since not guaranteed in alters_db_schema
    pg_test_orm._db.create_db()

    _test_create_schema(pg_test_orm, pg_test_orm._create_schema_datafeed_src,
            'datafeed_src')
    pg_test_orm._db._conn.close()
