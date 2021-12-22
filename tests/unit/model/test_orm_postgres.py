#!/usr/bin/env python3
"""
Tests the grand_trade_auto.model.orm_postgres functionality.

Per [pytest](https://docs.pytest.org/en/reorganize-docs/new-docs/user/naming_conventions.html),
all tiles, classes, and methods will be prefaced with `test_/Test` to comply
with auto-discovery (others may exist, but will not be part of test suite
directly).

Module Attributes:
  logger (Logger): Logger for this module (used for testing).

(C) Copyright 2021 Jonathan Casey.  All Rights Reserved Worldwide.
"""
#pylint: disable=protected-access  # Allow for purpose of testing those elements

import logging
import re
import uuid

import psycopg2.errors
import pytest

from grand_trade_auto.database import databases
from grand_trade_auto.database import postgres
from grand_trade_auto.model import model_meta
from grand_trade_auto.model import orm_meta

from tests.unit import conftest as unit_conftest



logger = logging.getLogger(__name__)




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



@pytest.fixture(scope='module', autouse=True)
def fixture_create_test_table():
    """
    Creates a table in the test database for this test.

    This MUST match the TestModel class in this module.
    """
    test_db = databases._get_database_from_config(unit_conftest._TEST_PG_DB_ID,
            unit_conftest._TEST_PG_ENV)
    conn = test_db.connect(False)
    sql = '''
        CREATE TABLE test_orm_postgres (
            id integer NOT NULL GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            test_name text,
            str_data text,
            int_data integer
        )
    '''
    test_db.execute(sql, conn=conn)
    conn.close()



class ModelTest(model_meta.Model):
    """
    A test model to use for testing within this module.

    This MUST match with the `fixture_create_test_table` in this module.
    """
    _table_name = 'test_orm_postgres'

    _columns = (
        'id',
        'test_name',
        'str_data',
        'int_data',
    )

    # Don't need the attributes for each column -- not used



def test_add(monkeypatch, caplog, pg_test_orm):
    """
    Tests the `add()` method in `PostgresOrm`.
    """
    caplog.set_level(logging.WARNING)

    good_data = {
        'test_name': 'test_add',
        'str_data': str(uuid.uuid4()),
        'int_data': 1,
    }
    bad_id = {
        'id': 2,
        'test_name': 'test_add',
        'str_data': str(uuid.uuid4()),
        'int_data': 2,
    }
    bad_col = {
        'test_name': 'test_add',
        'str_data': str(uuid.uuid4()),
        'int_data': 3,
        'bad_col': 'nonexistent col'
    }
    bad_type = {
        'test_name': 'test_add',
        'str_data': str(uuid.uuid4()),
        'int_data': 'four',
    }

    conn_2 = pg_test_orm._db.connect(False)
    cursor_2 = pg_test_orm._db.cursor(conn=conn_2)
    sql_select = 'SELECT * FROM test_orm_postgres'

    pg_test_orm.add(ModelTest, good_data, cursor=cursor_2, close_cursor=False)
    cursor = pg_test_orm._db.execute(sql_select, cursor=cursor_2,
            close_cursor=False)
    assert cursor == cursor_2
    assert cursor.rowcount == 1
    cols = [d[0] for d in cursor.description]
    results = dict(zip(cols, cursor.fetchone()))
    assert results['str_data'] == good_data['str_data']
    cursor.close() # Effectively also closes cursor_2


    with pytest.raises(
            psycopg2.errors.GeneratedAlways           #pylint: disable=no-member
            ) as ex:
        pg_test_orm.add(ModelTest, bad_id)
    assert 'cannot insert into column "id"' in str(ex.value)

    with pytest.raises(orm_meta.NonexistentColumnError) as ex:
        pg_test_orm.add(ModelTest, bad_col)
    assert "Invalid columns for ModelTest: ['bad_col']" in str(ex.value)
    pg_test_orm._db._conn.rollback()

    with pytest.raises(
            psycopg2.errors.InvalidTextRepresentation #pylint: disable=no-member
            ) as ex:
        pg_test_orm.add(ModelTest, bad_type)
    assert 'invalid input syntax for type integer: "four"' in str(ex.value)

    def mock_execute(self, command, val_vars=None, cursor=None, commit=True,
            close_cursor=True, **kwargs):
        """
        Simply logs the mogrified SQL statement for inspection.
        """
        #pylint: disable=unused-argument
        cursor = self.connect().cursor()
        sql = cursor.mogrify(command, val_vars)
        self.connect().commit()
        cursor.close()
        sql_formatted = re.sub(rb'\n\s+', b' ', sql.strip())
        logger.warning(sql_formatted)

    monkeypatch.setattr(postgres.Postgres, 'execute', mock_execute)
    caplog.clear()
    pg_test_orm.add(ModelTest, good_data)
    assert caplog.record_tuples == [
        ('tests.unit.model.test_orm_postgres', logging.WARNING,
            'b"INSERT INTO test_orm_postgres (test_name,str_data,int_data)'
            + ' VALUES (\'test_add\','
            + f' \'{str(good_data["str_data"])}\', 1)"')
    ]

    conn_2.close()
    pg_test_orm._db._conn.close()
