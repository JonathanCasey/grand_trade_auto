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



@pytest.mark.alters_db_schema
@pytest.mark.order(1)
def test__create_schema_datafeed_src(pg_test_orm):
    """
    Tests the `_create_schema_datafeed_src()` method in `PostgresOrm`.
    """
    def _drop_own_table():
        sql_drop_table = 'DROP TABLE IF EXISTS datafeed_src'
        cursor = pg_test_orm._db.connect().cursor()
        cursor.execute(sql_drop_table)
        cursor.connection.commit()
        cursor.close()

    _drop_own_table()

    # Sanity check -- ensure table really does not exist
    sql_table_exists = '''
        SELECT EXISTS (
        SELECT FROM information_schema.tables
        WHERE  table_schema = 'public'
        AND    table_name   = 'datafeed_src'
    )
    '''
    cursor = pg_test_orm._db.execute(sql_table_exists, close_cursor=False)
    assert cursor.fetchone()[0] is False
    cursor.close()

    pg_test_orm._create_schema_datafeed_src()
    cursor = pg_test_orm._db.execute(sql_table_exists, close_cursor=False)
    assert cursor.fetchone()[0] is True
    cursor.close()

    _drop_own_table()
    pg_test_orm._db.connect().close()
