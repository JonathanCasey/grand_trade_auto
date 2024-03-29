#!/usr/bin/env python3
"""
Tests the integration between:
- grand_trade_auto.database.postgres
- grand_trade_auto.orm.postgres_orm

While unit tests already test this integration to some degree, this is to a more
exhaustive degree.  Those unit tests are mostly using integrative approaches due
to minimizing mock complexity and making tests practically useful, but do aim to
minimize how much of the integration is invoked.

Per [pytest](https://docs.pytest.org/en/reorganize-docs/new-docs/user/naming_conventions.html),
all tiles, classes, and methods will be prefaced with `test_/Test` to comply
with auto-discovery (others may exist, but will not be part of test suite
directly).

Module Attributes:
  logger (Logger): Logger for this module (used for testing).

(C) Copyright 2022 Jonathan Casey.  All Rights Reserved Worldwide.
"""
#pylint: disable=protected-access  # Allow for purpose of testing those elements

import logging
import uuid

import psycopg2.errors
import pytest

from grand_trade_auto.database import databases
from grand_trade_auto.model import model_meta
from grand_trade_auto.orm import orm_meta

from tests import conftest as tests_conftest



logger = logging.getLogger(__name__)



@pytest.fixture(scope='module', autouse=True)
def fixture_create_test_table():
    """
    Creates a table in the test database for this test.

    This MUST match the TestModel class in this module.
    """
    test_db = databases._get_database_from_config(tests_conftest._TEST_PG_DB_ID,
            tests_conftest._TEST_PG_ENV)
    conn = test_db.connect(False)
    sql = '''
        CREATE TABLE test_int__postgres_orm (
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
    _table_name = 'test_int__postgres_orm'

    _columns = (
        'id',
        'test_name',
        'str_data',
        'int_data',
        'bool_data',
    )

    _read_only_columns = (
        'id',
    )

    # Don't need the attributes for each column -- not used



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



def test_add(caplog, pg_test_orm):
    """
    Tests the `add()` method in `PostgresOrm`.
    """
    #pylint: disable=too-many-locals

    caplog.set_level(logging.WARNING)

    test_name = 'test_add'
    good_data = {
        'test_name': test_name,
        'str_data': str(uuid.uuid4()),
        'int_data': 1,
        'bool_data': True,
    }
    bad_id_ro = {
        'id': 2,
        'test_name': test_name,
        'str_data': str(uuid.uuid4()),
        'int_data': 2,
        'bool_data': True,
    }
    bad_type = {
        'test_name': test_name,
        'str_data': str(uuid.uuid4()),
        'int_data': 'four',
        'bool_data': True,
    }

    conn_2 = pg_test_orm._db.connect(False)
    cursor_2 = pg_test_orm._db.cursor(conn=conn_2)
    sql_select = 'SELECT * FROM test_int__postgres_orm' \
            + ' WHERE test_name=%(test_name)s'
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
        pg_test_orm.add(ModelTest, bad_id_ro)
    assert 'cannot insert into column "id"' in str(ex.value)
    pg_test_orm._db._conn.rollback()

    # Ensure bad type in new data is caught
    with pytest.raises(
            psycopg2.errors.InvalidTextRepresentation #pylint: disable=no-member
            ) as ex:
        pg_test_orm.add(ModelTest, bad_type)
    assert 'invalid input syntax for type integer: "four"' in str(ex.value)

    conn_2.close()
    pg_test_orm._db._conn.close()



def test_update(caplog, pg_test_orm):
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
        {
            'str_data': str(uuid.uuid4()),
        },
    ]
    bad_id_ro = {
        'id': 3,
        'test_name': test_name,
        'str_data': str(uuid.uuid4()),
        'int_data': 3,
        'bool_data': True,
    }
    bad_type = {
        'test_name': test_name,
        'str_data': str(uuid.uuid4()),
        'int_data': 'five',
        'bool_data': True,
    }

    sql_select = '''
        SELECT * FROM test_int__postgres_orm
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

    # Ensure all updated if where empty
    pg_test_orm.update(ModelTest, new_data[2], None)
    cursor = pg_test_orm._db.execute(sql_select, select_var_vals,
            close_cursor=False)
    assert cursor.rowcount == 2
    cols = [d[0] for d in cursor.description]
    for i in range(cursor.rowcount):
        results = dict(zip(cols, cursor.fetchone()))
        results.pop('id')
        assert results == {**init_data[i], **new_data[1], **new_data[2]}
    cursor.close()

    # Ensure cannot update id col
    with pytest.raises(
            psycopg2.errors.GeneratedAlways           #pylint: disable=no-member
            ) as ex:
        pg_test_orm.update(ModelTest, bad_id_ro, where_1)
    assert 'column "id" can only be updated to DEFAULT\nDETAIL:  Column "id"' \
            + ' is an identity column defined as GENERATED ALWAYS.' \
            in str(ex.value)
    pg_test_orm._db._conn.rollback()

    # Ensure bad type in new data is caught
    with pytest.raises(
            psycopg2.errors.InvalidTextRepresentation #pylint: disable=no-member
            ) as ex:
        pg_test_orm.update(ModelTest, bad_type, where_1)
    assert 'invalid input syntax for type integer: "five"' in str(ex.value)

    conn_2.close()
    pg_test_orm._db._conn.close()



def test_delete(caplog, pg_test_orm):
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
        SELECT * FROM test_int__postgres_orm
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

    # Ensure delete all works with explicit delete all
    _load_data_and_confirm(pg_test_orm, init_data, sql_select, select_var_vals)
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
        ('grand_trade_auto.orm.postgres_orm', logging.ERROR,
            "Invalid column(s) for ModelTest: `bad_col`"),
    ]

    # Ensure bad type in where is caught
    where_bad_type = ('id', model_meta.LogicOp.GTE, 'nan')
    with pytest.raises(
            psycopg2.errors.InvalidTextRepresentation #pylint: disable=no-member
            ) as ex:
        pg_test_orm.delete(ModelTest, where_bad_type)
    assert 'invalid input syntax for type integer: "nan"' in str(ex.value)

    conn_2.close()
    pg_test_orm._db._conn.close()



def test_query(caplog, pg_test_orm):
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
        SELECT * FROM test_int__postgres_orm
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

    # Ensure bad col in where caught
    caplog.clear()
    where_bad_col = ('bad_col', model_meta.LogicOp.NOT_NULL)
    with pytest.raises(orm_meta.NonexistentColumnError) as ex:
        pg_test_orm.query(ModelTest, 'model', where=where_bad_col)
    assert "Invalid column(s) for ModelTest: `bad_col`" in str(ex.value)
    assert caplog.record_tuples == [
        ('grand_trade_auto.orm.postgres_orm', logging.ERROR,
            "Invalid column(s) for ModelTest: `bad_col`"),
    ]

    # Ensure bad type anywhere is caught
    where_bad_type = ('id', model_meta.LogicOp.GTE, 'nan')
    with pytest.raises(
            psycopg2.errors.InvalidTextRepresentation #pylint: disable=no-member
            ) as ex:
        pg_test_orm.query(ModelTest, 'pandas', where=where_bad_type)
    assert 'invalid input syntax for type integer: "nan"' in str(ex.value)

    conn_2.close()
    pg_test_orm._db._conn.close()
