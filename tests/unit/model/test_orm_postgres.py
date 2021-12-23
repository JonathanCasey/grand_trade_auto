#!/usr/bin/env python3
"""
Tests the grand_trade_auto.model.orm_postgres functionality.

Note that most of these tests are NOT intended to be run in parallel -- changes
would need to be made to ensure they do not conflict with the state of the
database (probably easiest to make a dedicated table for each test).

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
from grand_trade_auto.model import orm_postgres

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
@pytest.mark.order(-2)
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
            int_data integer,
            bool_data boolean
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
        'bool_data',
    )

    # Don't need the attributes for each column -- not used



def mock_execute_log(self, command, val_vars=None, cursor=None, commit=True,
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



def _confirm_all_data(orm, data, sql_select, select_var_vals):
    """
    Confirms the data struct is loaded in the table and is the only thing loaded
    in the table.
    """
    conn = orm._db.connect(False)
    cursor = orm._db.execute(sql_select, select_var_vals,
            close_cursor=False, conn=conn)
    assert cursor.rowcount == len(data)
    cols = [d[0] for d in cursor.description]
    for i in range(cursor.rowcount):
        results = dict(zip(cols, cursor.fetchone()))
        results.pop('id')
        assert results == data[i]
    cursor.close()
    conn.close()



def _load_data_and_confirm(orm, data, sql_select, select_var_vals):
    """
    Load data in table and confirm it is there.  Table expected to be empty
    prior to call.
    """
    conn = orm._db.connect(False)
    for d in data:
        orm.add(ModelTest, d, conn=conn)
    conn.close()
    _confirm_all_data(orm, data, sql_select, select_var_vals)



def test_add(monkeypatch, caplog, pg_test_orm):
    """
    Tests the `add()` method in `PostgresOrm`.
    """
    caplog.set_level(logging.WARNING)

    test_name = 'test_add'
    good_data = {
        'test_name': test_name,
        'str_data': str(uuid.uuid4()),
        'int_data': 1,
        'bool_data': True,
    }
    bad_id = {
        'id': 2,
        'test_name': test_name,
        'str_data': str(uuid.uuid4()),
        'int_data': 2,
        'bool_data': True,
    }
    bad_col = {
        'test_name': test_name,
        'str_data': str(uuid.uuid4()),
        'int_data': 3,
        'bool_data': True,
        'bad_col': 'nonexistent col'
    }
    bad_type = {
        'test_name': test_name,
        'str_data': str(uuid.uuid4()),
        'int_data': 'four',
        'bool_data': True,
    }

    conn_2 = pg_test_orm._db.connect(False)
    cursor_2 = pg_test_orm._db.cursor(conn=conn_2)
    sql_select = 'SELECT * FROM test_orm_postgres WHERE test_name=%(test_name)s'
    select_var_vals = {'test_name': test_name}

    # Ensure single row add; can supply a cursor, keep it open
    pg_test_orm.add(ModelTest, good_data, cursor=cursor_2, close_cursor=False)
    cursor = pg_test_orm._db.execute(sql_select, select_var_vals,
            cursor=cursor_2, close_cursor=False)
    assert cursor == cursor_2
    assert cursor.rowcount == 1
    cols = [d[0] for d in cursor.description]
    results = dict(zip(cols, cursor.fetchone()))
    assert results['str_data'] == good_data['str_data']
    cursor.close() # Effectively also closes cursor_2

    # Ensure cannot set id col
    with pytest.raises(
            psycopg2.errors.GeneratedAlways           #pylint: disable=no-member
            ) as ex:
        pg_test_orm.add(ModelTest, bad_id)
    assert 'cannot insert into column "id"' in str(ex.value)
    pg_test_orm._db._conn.rollback()

    # Ensure bad col in new data caught
    caplog.clear()
    with pytest.raises(orm_meta.NonexistentColumnError) as ex:
        pg_test_orm.add(ModelTest, bad_col)
    assert "Invalid column(s) for ModelTest: `bad_col`" in str(ex.value)
    assert caplog.record_tuples == [
        ('grand_trade_auto.model.orm_postgres', logging.ERROR,
            "Invalid column(s) for ModelTest: `bad_col`"),
    ]

    # Ensure bad type in new data is caught
    with pytest.raises(
            psycopg2.errors.InvalidTextRepresentation #pylint: disable=no-member
            ) as ex:
        pg_test_orm.add(ModelTest, bad_type)
    assert 'invalid input syntax for type integer: "four"' in str(ex.value)

    # Ensure SQL generated as expected
    monkeypatch.setattr(postgres.Postgres, 'execute', mock_execute_log)
    caplog.clear()
    pg_test_orm.add(ModelTest, good_data)
    assert caplog.record_tuples == [
        ('tests.unit.model.test_orm_postgres', logging.WARNING,
            'b"INSERT INTO test_orm_postgres'
            + ' (test_name,str_data,int_data,bool_data)'
            + ' VALUES (\'test_add\','
            + f' \'{str(good_data["str_data"])}\', 1, true)"'),
    ]

    conn_2.close()
    pg_test_orm._db._conn.close()



def test_update(monkeypatch, caplog, pg_test_orm):
    """
    Tests the `update()` method in `PostgresOrm`.
    """
    #pylint: disable=too-many-locals, too-many-statements
    caplog.set_level(logging.WARNING)

    test_name = 'test_update'
    init_data = [
        {
            'test_name': test_name,
            'str_data': str(uuid.uuid4()),
            'int_data': 1,
            'bool_data': True,
        },
        {
            'test_name': test_name,
            'str_data': str(uuid.uuid4()),
            'int_data': 2,
            'bool_data': True,
        },
    ]
    new_data = [
        {
            'str_data': str(uuid.uuid4()),
        },
        {
            'str_data': str(uuid.uuid4()),
            'bool_data': False,
        },
    ]
    bad_id = {
        'id': 3,
        'test_name': test_name,
        'str_data': str(uuid.uuid4()),
        'int_data': 3,
        'bool_data': True,
    }
    bad_col = {
        'test_name': test_name,
        'str_data': str(uuid.uuid4()),
        'int_data': 4,
        'bool_data': True,
        'bad_col': 'nonexistent col'
    }
    bad_type = {
        'test_name': test_name,
        'str_data': str(uuid.uuid4()),
        'int_data': 'five',
        'bool_data': True,
    }

    sql_select = '''
        SELECT * FROM test_orm_postgres
        WHERE test_name=%(test_name)s
        ORDER BY id
    '''
    select_var_vals = {'test_name': test_name}

    _load_data_and_confirm(pg_test_orm, init_data, sql_select, select_var_vals)

    # Ensure simple where; single row update; can supply a cursor, keep it open
    conn_2 = pg_test_orm._db.connect(False)
    cursor_2 = pg_test_orm._db.cursor(conn=conn_2)
    where_1 = ('int_data', model_meta.LogicOp.EQ, 1)
    pg_test_orm.update(ModelTest, new_data[0], where_1, cursor=cursor_2,
            close_cursor=False)
    cursor = pg_test_orm._db.execute(sql_select, select_var_vals,
            cursor=cursor_2, close_cursor=False)
    assert cursor == cursor_2
    assert cursor.rowcount == 2
    cols = [d[0] for d in cursor.description]
    for i in range(cursor.rowcount):
        results = dict(zip(cols, cursor.fetchone()))
        results.pop('id')
        if i == 0:
            assert results == {**init_data[i], **new_data[0]}
        else:
            assert results == init_data[i]
    cursor_2.close() # Effectively also closes cursor_2

    # Ensure complex where, multiple rows updated to same vals
    where_1_2 = {
        model_meta.LogicCombo.OR: [
            ('int_data', model_meta.LogicOp.EQ, 1),
            ('int_data', model_meta.LogicOp.EQ, 2),
        ],
    }
    pg_test_orm.update(ModelTest, new_data[1], where_1_2)
    cursor = pg_test_orm._db.execute(sql_select, select_var_vals,
            close_cursor=False)
    assert cursor.rowcount == 2
    cols = [d[0] for d in cursor.description]
    for i in range(cursor.rowcount):
        results = dict(zip(cols, cursor.fetchone()))
        results.pop('id')
        assert results == {**init_data[i], **new_data[1]}
    cursor.close()

    # Ensure cannot update id col
    with pytest.raises(
            psycopg2.errors.GeneratedAlways           #pylint: disable=no-member
            ) as ex:
        pg_test_orm.update(ModelTest, bad_id, where_1)
    assert 'column "id" can only be updated to DEFAULT\nDETAIL:  Column "id"' \
            + ' is an identity column defined as GENERATED ALWAYS.' \
            in str(ex.value)
    pg_test_orm._db._conn.rollback()

    # Ensure bad col in new data caught
    caplog.clear()
    with pytest.raises(orm_meta.NonexistentColumnError) as ex:
        pg_test_orm.update(ModelTest, bad_col, where_1)
    assert "Invalid column(s) for ModelTest: `bad_col`" in str(ex.value)
    assert caplog.record_tuples == [
        ('grand_trade_auto.model.orm_postgres', logging.ERROR,
            "Invalid column(s) for ModelTest: `bad_col`"),
    ]

    # Ensure bad type in new data is caught
    with pytest.raises(
            psycopg2.errors.InvalidTextRepresentation #pylint: disable=no-member
            ) as ex:
        pg_test_orm.update(ModelTest, bad_type, where_1)
    assert 'invalid input syntax for type integer: "five"' in str(ex.value)

    # Ensure SQL generated as expected
    monkeypatch.setattr(postgres.Postgres, 'execute', mock_execute_log)
    caplog.clear()
    pg_test_orm.update(ModelTest, new_data[1], where_1_2)
    assert caplog.record_tuples == [
        ('tests.unit.model.test_orm_postgres', logging.WARNING,
            'b"UPDATE test_orm_postgres SET str_data = \''
            + f'{new_data[1]["str_data"]}\', bool_data = false WHERE'
            + ' (int_data = 1 OR int_data = 2)"'),
    ]

    conn_2.close()
    pg_test_orm._db._conn.close()



def test_delete(monkeypatch, caplog, pg_test_orm):
    """
    Tests the `delete()` method in `PostgresOrm`.
    """
    #pylint: disable=too-many-locals, too-many-statements
    caplog.set_level(logging.WARNING)

    test_name = 'test_delete'
    init_data = [
        {
            'test_name': test_name,
            'str_data': str(uuid.uuid4()),
            'int_data': 1,
            'bool_data': True,
        },
        {
            'test_name': test_name,
            'str_data': str(uuid.uuid4()),
            'int_data': 2,
            'bool_data': True,
        },
        {
            'test_name': test_name,
            'str_data': str(uuid.uuid4()),
            'int_data': 3,
            'bool_data': True,
        },
    ]

    sql_select = '''
        SELECT * FROM test_orm_postgres
        WHERE test_name=%(test_name)s
        ORDER BY id
    '''
    select_var_vals = {'test_name': test_name}

    _load_data_and_confirm(pg_test_orm, init_data, sql_select, select_var_vals)

    # Ensure simple where; can supply a cursor, keep it open
    conn_2 = pg_test_orm._db.connect(False)
    cursor_2 = pg_test_orm._db.cursor(conn=conn_2)
    where_1 = ('int_data', model_meta.LogicOp.EQ, 1)
    pg_test_orm.delete(ModelTest, where_1, cursor=cursor_2, close_cursor=False)
    cursor = pg_test_orm._db.execute(sql_select, select_var_vals,
            cursor=cursor_2, close_cursor=False)
    assert cursor == cursor_2
    assert cursor.rowcount == 2
    cols = [d[0] for d in cursor.description]
    for i in range(cursor.rowcount):
        results = dict(zip(cols, cursor.fetchone()))
        results.pop('id')
        assert results == init_data[i+1]
    cursor_2.close() # Effectively also closes cursor_2

    # Ensure complex where
    where_2_3 = {
        model_meta.LogicCombo.OR: [
            ('int_data', model_meta.LogicOp.EQ, 2),
            ('int_data', model_meta.LogicOp.EQ, 3),
        ],
    }
    pg_test_orm.delete(ModelTest, where_2_3)
    cursor = pg_test_orm._db.execute(sql_select, select_var_vals,
            close_cursor=False)
    assert cursor.rowcount == 0
    cursor.close()

    # Ensure delete all fails without explicit delete all
    _load_data_and_confirm(pg_test_orm, init_data, sql_select, select_var_vals)
    caplog.clear()
    with pytest.raises(ValueError) as ex:
        pg_test_orm.delete(ModelTest, {})
    assert 'Invalid delete parameters: `where` empty, but' in str(ex.value)
    assert caplog.record_tuples == [
        ('grand_trade_auto.model.orm_postgres', logging.ERROR,
            'Invalid delete parameters: `where` empty, but did not'
                    + ' set `really_delete_all` to confirm delete all.'
                    + '  Likely intended to specify `where`?'),
    ]

    # Ensure delete all works with explicit delete all
    _confirm_all_data(pg_test_orm, init_data, sql_select, select_var_vals)
    pg_test_orm.delete(ModelTest, None, really_delete_all=True)
    cursor = pg_test_orm._db.execute(sql_select, select_var_vals,
            close_cursor=False)
    assert cursor.rowcount == 0
    cursor.close()

    # Ensure bad col in where caught
    caplog.clear()
    where_bad_col = ('bad_col', model_meta.LogicOp.NOT_NULL)
    with pytest.raises(orm_meta.NonexistentColumnError) as ex:
        pg_test_orm.delete(ModelTest, where_bad_col)
    assert "Invalid column(s) for ModelTest: `bad_col`" in str(ex.value)
    assert caplog.record_tuples == [
        ('grand_trade_auto.model.orm_postgres', logging.ERROR,
            "Invalid column(s) for ModelTest: `bad_col`"),
    ]

    # Ensure bad type in where is caught
    where_bad_type = ('id', model_meta.LogicOp.GTE, 'nan')
    with pytest.raises(
            psycopg2.errors.InvalidTextRepresentation #pylint: disable=no-member
            ) as ex:
        pg_test_orm.delete(ModelTest, where_bad_type)
    assert 'invalid input syntax for type integer: "nan"' in str(ex.value)

    # Ensure SQL generated as expected
    monkeypatch.setattr(postgres.Postgres, 'execute', mock_execute_log)
    caplog.clear()
    pg_test_orm.delete(ModelTest, where_2_3)
    assert caplog.record_tuples == [
        ('tests.unit.model.test_orm_postgres', logging.WARNING,
            "b'DELETE FROM test_orm_postgres WHERE"
            + " (int_data = 2 OR int_data = 3)'"),
    ]

    conn_2.close()
    pg_test_orm._db._conn.close()



def test_query(monkeypatch, caplog, pg_test_orm):
    """
    Tests the `query()` method in `PostgresOrm`.
    """
    #pylint: disable=too-many-locals, too-many-statements
    caplog.set_level(logging.WARNING)

    test_name = 'test_query'
    init_data = [
        {
            'test_name': test_name,
            'str_data': str(uuid.uuid4()),
            'int_data': 1,
            'bool_data': True,
        },
        {
            'test_name': test_name,
            'str_data': str(uuid.uuid4()),
            'int_data': 2,
            'bool_data': True,
        },
        {
            'test_name': test_name,
            'str_data': str(uuid.uuid4()),
            'int_data': 3,
            'bool_data': False,
        },
        {
            'test_name': test_name,
            'str_data': str(uuid.uuid4()),
            'int_data': 4,
            'bool_data': True,
        },
    ]

    sql_select = '''
        SELECT * FROM test_orm_postgres
        WHERE test_name=%(test_name)s
        ORDER BY id
    '''
    select_var_vals = {'test_name': test_name}

    _load_data_and_confirm(pg_test_orm, init_data, sql_select, select_var_vals)

    # Ensure good without where clause; cursor closed; return as pandas(enum)
    cursor = pg_test_orm._db.cursor()
    pd_df = pg_test_orm.query(ModelTest, model_meta.ReturnAs.PANDAS,
            cursor=cursor, close_cursor=True)
    assert cursor.closed is True
    assert len(pd_df['test_name']==test_name) >= len(init_data)

    # Ensure can supply a cursor, keep it open; and return as model(enum)
    conn_2 = pg_test_orm._db.connect(False)
    cursor_2 = pg_test_orm._db.cursor(conn=conn_2)
    where_1 = ('int_data', model_meta.LogicOp.EQ, 1)
    models = pg_test_orm.query(ModelTest, model_meta.ReturnAs.MODEL,
            ModelTest._columns, where_1, cursor=cursor_2, close_cursor=False)
    assert cursor_2.rowcount == 1
    init_data_model_indices = [0]
    assert len(models) == len(init_data_model_indices)
    for i, mdl in enumerate(models):
        for k, v in init_data[init_data_model_indices[i]].items():
            assert getattr(mdl, k) == v
        assert isinstance(mdl.id, int)
    cursor_2.close() # Effectively also closes cursor_2

    # Ensure more complex where; with cols, order, limit; return pandas(str)
    where_2_3 = {
        model_meta.LogicCombo.OR: [
            ('int_data', model_meta.LogicOp.EQ, 2),
            ('int_data', model_meta.LogicOp.EQ, 3),
        ],
    }
    cols_to_return = ['id', 'int_data']
    order_id_desc = [('id', model_meta.SortOrder.DESC)]
    limit = len(init_data)
    pd_df = pg_test_orm.query(ModelTest, 'pandas', cols_to_return, where_2_3,
            limit, order_id_desc)
    init_data_model_indices = [2, 1]
    assert len(pd_df) == len(init_data_model_indices)
    assert list(pd_df.columns) == cols_to_return
    min_id_so_far = 65535   # Must be much larger than anything expected
    for i in range(len(pd_df)):
        for k, v in init_data[init_data_model_indices[i]].items():
            if k not in cols_to_return or k == 'id':
                continue
            assert pd_df.iloc[i].loc[k] == v
        try:
            pd_id = int(pd_df.iloc[i].loc['id'])
        except ValueError:
            assert False
        assert pd_id == pd_df.iloc[i].loc['id']
        assert pd_id < min_id_so_far
        min_id_so_far = pd_id

    # Ensure complex order; effective limit; cursor closed; return model(str)
    cursor = pg_test_orm._db.cursor()
    order_bool_asc_int_desc = [
        ('bool_data', model_meta.SortOrder.ASC),
        ('int_data', model_meta.SortOrder.DESC),
    ]
    limit = len(init_data) - 1
    models = pg_test_orm.query(ModelTest, 'model', limit=limit,
            order=order_bool_asc_int_desc, cursor=cursor)
    assert cursor.closed is True
    init_data_model_indices = [2, 3, 1]
    assert len(models) == len(init_data_model_indices)
    for i, mdl in enumerate(models):
        for k, v in init_data[init_data_model_indices[i]].items():
            assert getattr(mdl, k) == v
        assert isinstance(mdl.id, int)

    # Ensure invalid return as caught
    with pytest.raises(ValueError) as ex:
        pg_test_orm.query(ModelTest, 'invalid-return-as')
    assert "'invalid-return-as' is not a valid ReturnAs" in str(ex.value)

    # Ensure bad col in return cols caught
    caplog.clear()
    with pytest.raises(orm_meta.NonexistentColumnError) as ex:
        pg_test_orm.query(ModelTest, 'model', ['bad_col'])
    assert "Invalid column(s) for ModelTest: `bad_col`" in str(ex.value)
    assert caplog.record_tuples == [
        ('grand_trade_auto.model.orm_postgres', logging.ERROR,
            "Invalid column(s) for ModelTest: `bad_col`"),
    ]

    # Ensure bad col in where caught
    caplog.clear()
    where_bad_col = ('bad_col', model_meta.LogicOp.NOT_NULL)
    with pytest.raises(orm_meta.NonexistentColumnError) as ex:
        pg_test_orm.query(ModelTest, 'model', where=where_bad_col)
    assert "Invalid column(s) for ModelTest: `bad_col`" in str(ex.value)
    assert caplog.record_tuples == [
        ('grand_trade_auto.model.orm_postgres', logging.ERROR,
            "Invalid column(s) for ModelTest: `bad_col`"),
    ]

    # Ensure bad col in order caught
    caplog.clear()
    order_bad_col = [('bad_col', model_meta.SortOrder.ASC)]
    with pytest.raises(orm_meta.NonexistentColumnError) as ex:
        pg_test_orm.query(ModelTest, 'model', order=order_bad_col)
    assert "Invalid column(s) for ModelTest: `bad_col`" in str(ex.value)
    assert caplog.record_tuples == [
        ('grand_trade_auto.model.orm_postgres', logging.ERROR,
            "Invalid column(s) for ModelTest: `bad_col`"),
    ]

    # Ensure bad limit arg caught
    caplog.clear()
    with pytest.raises(ValueError) as ex:
        pg_test_orm.query(ModelTest, 'model', limit='nan')
    assert "Failed to limit, likely not a number:" in str(ex.value)
    assert caplog.record_tuples == [
        ('grand_trade_auto.model.orm_postgres', logging.ERROR,
            "Failed to limit, likely not a number: invalid literal for int()"
            + " with base 10: 'nan'"),
    ]

    # Ensure bad type anywhere is caught
    where_bad_type = ('id', model_meta.LogicOp.GTE, 'nan')
    with pytest.raises(
            psycopg2.errors.InvalidTextRepresentation #pylint: disable=no-member
            ) as ex:
        pg_test_orm.query(ModelTest, 'pandas', where=where_bad_type)
    assert 'invalid input syntax for type integer: "nan"' in str(ex.value)

    # Ensure SQL generated as expected
    monkeypatch.setattr(postgres.Postgres, 'execute', mock_execute_log)
    caplog.clear()
    # Don't really care about exception -- just side effect of mock
    with pytest.raises(AttributeError):
        pg_test_orm.query(ModelTest, 'model', where=where_2_3, limit=100,
                order=order_bool_asc_int_desc)
    assert caplog.record_tuples == [
        ('tests.unit.model.test_orm_postgres', logging.WARNING,
            "b'SELECT * FROM test_orm_postgres WHERE (int_data = 2 OR"
            + " int_data = 3) ORDER BY bool_data ASC, int_data DESC"
            + " LIMIT 100'"),
    ]

    conn_2.close()
    pg_test_orm._db._conn.close()



def test__convert_cursor_to_models(pg_test_orm):
    """
    Tests the `_convert_cursor_to_models()` method in `PostgresOrm`.
    """
    test_name = 'test__convert_cursor_to_models'
    init_data = [
        {
            'test_name': test_name,
            'str_data': str(uuid.uuid4()),
            'int_data': 1,
            'bool_data': True,
        },
        {
            'test_name': test_name,
            'str_data': str(uuid.uuid4()),
            'int_data': 2,
            'bool_data': True,
        },
        {
            'test_name': test_name,
            'str_data': str(uuid.uuid4()),
            'int_data': 3,
            'bool_data': False,
        },
    ]

    sql_select = '''
        SELECT * FROM test_orm_postgres
        WHERE test_name=%(test_name)s
        ORDER BY id
    '''
    select_var_vals = {'test_name': test_name}

    _load_data_and_confirm(pg_test_orm, init_data, sql_select, select_var_vals)

    cursor = pg_test_orm._db.execute(sql_select, select_var_vals,
            close_cursor=False)
    models = pg_test_orm._convert_cursor_to_models(ModelTest, cursor)
    assert cursor.rowcount == 3
    assert len(models) == len(init_data)
    for i, mdl in enumerate(models):
        for k, v in init_data[i].items():
            assert getattr(mdl, k) == v
        assert isinstance(mdl.id, int)

    cursor.close()
    pg_test_orm._db._conn.close()



def test__convert_cursor_to_pandas_dataframe(pg_test_orm):
    """
    Tests the `_convert_cursor_to_pandas_dataframe()` method in `PostgresOrm`.
    """
    test_name = 'test__convert_cursor_to_pandas_dataframe'
    init_data = [
        {
            'test_name': test_name,
            'str_data': str(uuid.uuid4()),
            'int_data': 1,
            'bool_data': True,
        },
        {
            'test_name': test_name,
            'str_data': str(uuid.uuid4()),
            'int_data': 2,
            'bool_data': True,
        },
        {
            'test_name': test_name,
            'str_data': str(uuid.uuid4()),
            'int_data': 3,
            'bool_data': False,
        },
    ]

    sql_select = '''
        SELECT * FROM test_orm_postgres
        WHERE test_name=%(test_name)s
        ORDER BY id
    '''
    select_var_vals = {'test_name': test_name}

    _load_data_and_confirm(pg_test_orm, init_data, sql_select, select_var_vals)

    cursor = pg_test_orm._db.execute(sql_select, select_var_vals,
            close_cursor=False)
    pd_df = pg_test_orm._convert_cursor_to_pandas_dataframe(cursor)
    assert len(pd_df) == len(init_data)
    assert set(pd_df.columns) == set(ModelTest._columns)
    for i in range(len(pd_df)):
        for k, v in init_data[i].items():
            if k == 'id':
                continue
            assert pd_df.iloc[i].loc[k] == v
        try:
            pd_id = int(pd_df.iloc[i].loc['id'])
        except ValueError:
            assert False
        assert pd_id == pd_df.iloc[i].loc['id']

    cursor.close()
    pg_test_orm._db._conn.close()



def test__validate_cols(caplog):
    """
    Tests the `_validate_cols()` in `orm_postgres`.
    """
    caplog.set_level(logging.WARNING)

    bad_cols = [
        'bad_col_1',
        'bad_col_2',
    ]

    # Ensure works with good columns, including with a subset of them
    orm_postgres._validate_cols(ModelTest._columns, ModelTest)
    orm_postgres._validate_cols(ModelTest._columns[1:3], ModelTest)

    caplog.clear()
    with pytest.raises(orm_meta.NonexistentColumnError) as ex:
        orm_postgres._validate_cols([*ModelTest._columns[1:2], bad_cols[0]],
                ModelTest)
    assert 'Invalid column(s) for ModelTest:' in str(ex.value)
    assert caplog.record_tuples == [
        ('grand_trade_auto.model.orm_postgres', logging.ERROR,
            "Invalid column(s) for ModelTest: `bad_col_1`"),
    ]

    caplog.clear()
    with pytest.raises(orm_meta.NonexistentColumnError) as ex:
        orm_postgres._validate_cols([*ModelTest._columns, *bad_cols], ModelTest)
    assert 'Invalid column(s) for ModelTest:' in str(ex.value)
    assert caplog.record_tuples[0][0] == 'grand_trade_auto.model.orm_postgres'
    assert caplog.record_tuples[0][1] == logging.ERROR
    # Since code under test uses set, order varies -- must compare as set
    msg_parts = caplog.record_tuples[0][2].split(': ', 1)
    assert msg_parts[0] == 'Invalid column(s) for ModelTest'
    assert set(msg_parts[1].split(', ')) == set([f'`{c}`' for c in bad_cols])
