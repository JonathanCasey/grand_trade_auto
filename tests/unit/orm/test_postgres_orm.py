#!/usr/bin/env python3
"""
Tests the grand_trade_auto.orm.postgres_orm functionality.

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
#pylint: disable=too-many-lines
#pylint: disable=use-implicit-booleaness-not-comparison
#   +-> want to specifically check type in most tests -- `None` is a fail

import itertools
import logging
import re
import uuid

import pandas as pd
import pytest

from grand_trade_auto.database import databases
from grand_trade_auto.database import postgres
from grand_trade_auto.model import model_meta
from grand_trade_auto.orm import orm_meta
from grand_trade_auto.orm import postgres_orm

from tests import conftest as tests_conftest



logger = logging.getLogger(__name__)



def _test_create_schema_enum(orm, test_func, enum_name, enum_cls,
        type_namespace=postgres_orm._TYPE_NAMESPACE, drop_enum_after=False):
    """
    A generic set of steps to test enum creation.

    This will alter the database schema for the database in the provided orm,
    ultimately possibly leaving the enum non-existent and definitely leaving
    dependent tables non-existent, so tests using this likely should be marked
    with alters_db_schema.

    This will use the cached connection of the Orm's db, so the caller must
    handle closing that connection.

    Args:
      orm (PostgresOrm): The PostgresOrm to use for this test.
      test_func (function): The create schema enum function to test, probably
        from that Orm.
      enum_name (str): The name of the enum that is being created.
      type_namespace (str): The name of the namespace of the enum that is being
        created.  Can likely use default unless it was changed elsewhere.
      drop_enum_after (bool): Whether or not to drop the enum after testing is
        complete.  Drop is cascaded, so dependent tables would also be dropped,
        but they should have already been dropped at start of this test.
    """
    #pylint: disable=too-many-locals

    def _drop_own_enum():
        """
        Drop the enum being created in this subtest.

        Despite the name, this MAY drop other tables if necessary via cascade.
        """
        sql_drop_enum = f'DROP TYPE IF EXISTS {enum_name} CASCADE'
        cursor = orm._db.connect().cursor()
        cursor.execute(sql_drop_enum)
        cursor.connection.commit()
        cursor.close()

    _drop_own_enum()

    sql_enum_exists = f'''
        WITH namespace AS (
            SELECT oid
            FROM pg_namespace
            WHERE nspname='{type_namespace}'
        ),
        type_name AS (
            SELECT 1 type_exists
            FROM pg_type
            WHERE typname='{enum_name}'
                AND typnamespace=(SELECT * FROM namespace)
        )
        SELECT EXISTS (SELECT * FROM type_name)
    '''

    # Sanity check -- ensure table really does not exist
    cursor = orm._db.execute(sql_enum_exists, close_cursor=False)
    assert cursor.fetchone()[0] is False
    cursor.close()

    test_func()
    cursor = orm._db.execute(sql_enum_exists, close_cursor=False)
    assert cursor.fetchone()[0] is True
    cursor.close()

    table_name = f'test_create_schema_enum__{enum_name}'
    col_name = 'test_enum'
    enum_item = list(enum_cls)[0]

    sql_create_table = f'CREATE TABLE {table_name} ({col_name} {enum_name})'
    orm._db.execute(sql_create_table)

    sql_insert = f'INSERT INTO {table_name} ({col_name}) VALUES (%(val)s)'
    orm._db.execute(sql_insert, {'val': enum_item})

    sql_query = f'SELECT {col_name} FROM {table_name}'
    cursor = orm._db.execute(sql_query, close_cursor=False)
    assert cursor.rowcount == 1
    assert cursor.fetchone()[0] is enum_item
    cursor.close()

    sql_drop_table = f'DROP TABLE {table_name}'
    orm._db.execute(sql_drop_table)

    if drop_enum_after:
        _drop_own_enum()



@pytest.mark.alters_db_schema
@pytest.mark.order(-2)      # After this, types exist, but maybe not tables/data
# Order of parameters must match order in _create_schemas() due to dependencies
@pytest.mark.parametrize('method_name, enum_name, enum_cls', [
    ('_create_schema_enum_currency', 'currency', model_meta.Currency),
    ('_create_schema_enum_market', 'market', model_meta.Market),
    ('_create_schema_enum_price_frequency', 'price_frequency',
            model_meta.PriceFrequency),
])
def test__create_schemas_enums(pg_test_orm, method_name, enum_name, enum_cls):
    """
    Tests the `_create_schema_enum_*()` methods in `PostgresOrm`.

    This also effectively tests the `_create_and_register_type_enum()` method in
    `PostgreOrm`.

    This should be run before any tests that drop the database (but can be run
    after any tests dropping tables).
    """
    _test_create_schema_enum(pg_test_orm, getattr(pg_test_orm, method_name),
            enum_name, enum_cls)
    pg_test_orm._db._conn.close()



def _test_create_schema_table(orm, test_func, table_name,
        schema_name=postgres_orm._SCHEMA_NAME, drop_table_after=False):
    """
    A generic set of steps to test table creation.

    This will alter the database schema for the database in the provided orm,
    ultimately possibly leaving the table non-existent, so tests using this
    likely should be marked with alters_db_schema.

    This will use the cached connection of the Orm's db, so the caller must
    handle closing that connection.

    Args:
      orm (PostgresOrm): The PostgresOrm to use for this test.
      test_func (function): The create schema function to test, probably from
        that Orm.
      table_name (str): The name of the table that is being created.
      schema_name (str): The schema name of the table that is being created.
        Can likely use default unless it was changed elsewhere.
      drop_table_after (bool): Whether or not to drop the table after testing is
        complete.
    """
    def _drop_own_table():
        """
        Drop the table being created in this subtest.

        Despite the name, this MAY drop other tables if necessary via cascade.
        """
        sql_drop_table = f'DROP TABLE IF EXISTS {table_name} CASCADE'
        cursor = orm._db.connect().cursor()
        cursor.execute(sql_drop_table)
        cursor.connection.commit()
        cursor.close()

    _drop_own_table()

    sql_table_exists = f'''
        SELECT EXISTS (
            SELECT 1
            FROM information_schema.tables
            WHERE  table_schema = '{schema_name}'
                AND    table_name   = '{table_name}'
        )
    '''

    # Sanity check -- ensure table really does not exist
    cursor = orm._db.execute(sql_table_exists, close_cursor=False)
    assert cursor.fetchone()[0] is False
    cursor.close()

    test_func()
    cursor = orm._db.execute(sql_table_exists, close_cursor=False)
    assert cursor.fetchone()[0] is True
    cursor.close()

    if drop_table_after:
        _drop_own_table()



@pytest.mark.alters_db_schema
@pytest.mark.order(-3)      # After this, tables/types exist, but maybe not data
# Order of parameters must match order in _create_schemas() due to dependencies
@pytest.mark.parametrize('method_name, table_name', [
    ('_create_schema_table_datafeed_src', 'datafeed_src'),
    ('_create_schema_table_company', 'company'),
    ('_create_schema_table_exchange', 'exchange'),
    ('_create_schema_table_security', 'security'),
    ('_create_schema_table_security_price', 'security_price'),
    ('_create_schema_table_stock_adjustment', 'stock_adjustment'),
])
def test__create_schemas_tables(pg_test_orm, method_name, table_name):
    """
    Tests the `_create_schema_table_*()` methods in `PostgresOrm`.

    This should be run before any tests that drop the database or types.
    """
    _test_create_schema_table(pg_test_orm, getattr(pg_test_orm, method_name),
            table_name)
    pg_test_orm._db._conn.close()



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
        CREATE TABLE test_postgres_orm (
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
    _table_name = 'test_postgres_orm'

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



def mock_execute_log(self, command, val_vars=None, cursor=None, commit=True,
            close_cursor=True, **kwargs):
    """
    Simply logs the mogrified SQL statement for inspection.
    """
    #pylint: disable=unused-argument
    cursor = cursor or self.connect().cursor()
    sql = cursor.mogrify(command, val_vars)
    if close_cursor:
        cursor.close()
    sql_formatted = re.sub(rb'\n\s+', b' ', sql.strip())
    logger.warning(sql_formatted)
    return cursor



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
    bad_col = {
        'test_name': test_name,
        'str_data': str(uuid.uuid4()),
        'int_data': 2,
        'bool_data': True,
        'bad_col': 'nonexistent col',
    }

    monkeypatch.setattr(postgres.Postgres, 'execute', mock_execute_log)

    caplog.clear()
    conn_2 = pg_test_orm._db.connect(False)
    cursor_2 = pg_test_orm._db.cursor(conn=conn_2)
    pg_test_orm.add(ModelTest, good_data, cursor=cursor_2, close_cursor=False)
    assert cursor_2.closed is False
    assert caplog.record_tuples == [
        ('tests.unit.orm.test_postgres_orm', logging.WARNING,
            'b"INSERT INTO test_postgres_orm'
            + ' (test_name,str_data,int_data,bool_data)'
            + ' VALUES (\'test_add\','
            + f' \'{str(good_data["str_data"])}\', 1, true)"'),
    ]
    cursor_2.close()

    caplog.clear()
    with pytest.raises(orm_meta.NonexistentColumnError) as ex:
        pg_test_orm.add(ModelTest, bad_col)
    assert "Invalid column(s) for ModelTest: `bad_col`" in str(ex.value)
    assert caplog.record_tuples == [
        ('grand_trade_auto.orm.postgres_orm', logging.ERROR,
            "Invalid column(s) for ModelTest: `bad_col`"),
    ]

    conn_2.close()



def test_update(monkeypatch, caplog, pg_test_orm):
    """
    Tests the `update()` method in `PostgresOrm`.
    """
    caplog.set_level(logging.WARNING)

    test_name = 'test_update'
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
    bad_col = {
        'test_name': test_name,
        'str_data': str(uuid.uuid4()),
        'int_data': 4,
        'bool_data': True,
        'bad_col': 'nonexistent col',
    }

    monkeypatch.setattr(postgres.Postgres, 'execute', mock_execute_log)

    caplog.clear()
    conn_2 = pg_test_orm._db.connect(False)
    cursor_2 = pg_test_orm._db.cursor(conn=conn_2)
    where_1 = ('int_data', model_meta.LogicOp.EQ, 1)
    pg_test_orm.update(ModelTest, new_data[0], where_1, cursor=cursor_2,
            close_cursor=False)
    assert cursor_2.closed is False
    assert caplog.record_tuples == [
        ('tests.unit.orm.test_postgres_orm', logging.WARNING,
            'b"UPDATE test_postgres_orm SET str_data = \''
            + f'{new_data[0]["str_data"]}\' WHERE int_data = 1"'),
    ]
    cursor_2.close()

    caplog.clear()
    pg_test_orm.update(ModelTest, new_data[1], None)
    assert caplog.record_tuples == [
        ('tests.unit.orm.test_postgres_orm', logging.WARNING,
            'b"UPDATE test_postgres_orm SET str_data = \''
            + f'{new_data[1]["str_data"]}\', bool_data = false"'),
    ]

    caplog.clear()
    with pytest.raises(orm_meta.NonexistentColumnError) as ex:
        pg_test_orm.update(ModelTest, bad_col, {})
    assert "Invalid column(s) for ModelTest: `bad_col`" in str(ex.value)
    assert caplog.record_tuples == [
        ('grand_trade_auto.orm.postgres_orm', logging.ERROR,
            "Invalid column(s) for ModelTest: `bad_col`"),
    ]

    conn_2.close()
    pg_test_orm._db._conn.close()



def test_delete(monkeypatch, caplog, pg_test_orm):
    """
    Tests the `delete()` method in `PostgresOrm`.
    """
    caplog.set_level(logging.WARNING)

    monkeypatch.setattr(postgres.Postgres, 'execute', mock_execute_log)

    caplog.clear()
    conn_2 = pg_test_orm._db.connect(False)
    cursor_2 = pg_test_orm._db.cursor(conn=conn_2)
    where_2_3 = {
        model_meta.LogicCombo.OR: [
            ('int_data', model_meta.LogicOp.EQ, 2),
            ('int_data', model_meta.LogicOp.EQ, 3),
        ],
    }
    pg_test_orm.delete(ModelTest, where_2_3, cursor=cursor_2,
            close_cursor=False)
    assert cursor_2.closed is False
    assert caplog.record_tuples == [
        ('tests.unit.orm.test_postgres_orm', logging.WARNING,
            "b'DELETE FROM test_postgres_orm WHERE"
            + " (int_data = 2 OR int_data = 3)'"),
    ]
    cursor_2.close()

    caplog.clear()
    pg_test_orm.delete(ModelTest, None, True)
    assert caplog.record_tuples == [
        ('tests.unit.orm.test_postgres_orm', logging.WARNING,
            "b'DELETE FROM test_postgres_orm'"),
    ]

    caplog.clear()
    with pytest.raises(ValueError) as ex:
        pg_test_orm.delete(ModelTest, {})
    assert 'Invalid delete parameters: `where` empty, but' in str(ex.value)
    assert caplog.record_tuples == [
        ('grand_trade_auto.orm.postgres_orm', logging.ERROR,
            'Invalid delete parameters: `where` empty, but did not'
                    + ' set `really_delete_all` to confirm delete all.'
                    + '  Likely intended to specify `where`?'),
    ]

    conn_2.close()
    pg_test_orm._db._conn.close()



def test_query(monkeypatch, caplog, pg_test_orm):
    """
    Tests the `query()` method in `PostgresOrm`.
    """
    #pylint: disable=too-many-locals, too-many-statements
    caplog.set_level(logging.WARNING)

    def mock_convert_cursor_to_models(self, model_cls, cursor):
        """
        Returns empty dummy values.
        """
        #pylint: disable=unused-argument
        return [ModelTest(postgres_orm.PostgresOrm(None))]

    def mock_convert_cursor_to_pandas_dataframe(cursor):
        """
        Returns empty dummy values.
        """
        #pylint: disable=unused-argument
        return pd.DataFrame()

    monkeypatch.setattr(postgres.Postgres, 'execute', mock_execute_log)
    monkeypatch.setattr(postgres_orm.PostgresOrm, '_convert_cursor_to_models',
            mock_convert_cursor_to_models)
    monkeypatch.setattr(postgres_orm.PostgresOrm,
            '_convert_cursor_to_pandas_dataframe',
            mock_convert_cursor_to_pandas_dataframe)

    caplog.clear()
    conn_2 = pg_test_orm._db.connect(False)
    cursor_2 = pg_test_orm._db.cursor(conn=conn_2)
    models = pg_test_orm.query(ModelTest, 'model', cursor=cursor_2,
            close_cursor=True)
    assert cursor_2.closed is True
    assert len(models) == 1
    assert isinstance(models[0], ModelTest)
    assert caplog.record_tuples == [
        ('tests.unit.orm.test_postgres_orm', logging.WARNING,
            "b'SELECT * FROM test_postgres_orm'"),
    ]

    caplog.clear()
    where_1 = ('int_data', model_meta.LogicOp.EQ, 1)
    order_id_desc = [('id', model_meta.SortOrder.DESC)]
    pd_df = pg_test_orm.query(ModelTest, model_meta.ReturnAs.PANDAS,
            ['str_data', 'int_data'], where_1, 3, order_id_desc)
    assert isinstance(pd_df, pd.DataFrame)
    assert caplog.record_tuples == [
        ('tests.unit.orm.test_postgres_orm', logging.WARNING,
            "b'SELECT str_data,int_data FROM test_postgres_orm"
            + " WHERE int_data = 1 ORDER BY id DESC LIMIT 3'"),
    ]

    caplog.clear()
    with pytest.raises(orm_meta.NonexistentColumnError) as ex:
        pg_test_orm.query(ModelTest, 'model', ['bad_col'])
    assert "Invalid column(s) for ModelTest: `bad_col`" in str(ex.value)
    assert caplog.record_tuples == [
        ('grand_trade_auto.orm.postgres_orm', logging.ERROR,
            "Invalid column(s) for ModelTest: `bad_col`"),
    ]

    caplog.clear()
    order_bad_col = [('bad_col', model_meta.SortOrder.ASC)]
    with pytest.raises(orm_meta.NonexistentColumnError) as ex:
        pg_test_orm.query(ModelTest, 'model', order=order_bad_col)
    assert "Invalid column(s) for ModelTest: `bad_col`" in str(ex.value)
    assert caplog.record_tuples == [
        ('grand_trade_auto.orm.postgres_orm', logging.ERROR,
            "Invalid column(s) for ModelTest: `bad_col`"),
    ]

    caplog.clear()
    with pytest.raises(ValueError) as ex:
        pg_test_orm.query(ModelTest, 'model', limit='nan')
    assert "Failed to parse limit, likely not a number:" in str(ex.value)
    assert caplog.record_tuples == [
        ('grand_trade_auto.orm.postgres_orm', logging.ERROR,
            "Failed to parse limit, likely not a number:"
            + " invalid literal for int() with base 10: 'nan'"),
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
        SELECT * FROM test_postgres_orm
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
        SELECT * FROM test_postgres_orm
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
    Tests the `_validate_cols()` method in `postgres_orm`.
    """
    caplog.set_level(logging.WARNING)

    bad_cols = [
        'bad_col_1',
        'bad_col_2',
    ]

    # Ensure works with good columns, including with a subset of them
    postgres_orm._validate_cols(ModelTest._columns, ModelTest)
    postgres_orm._validate_cols(ModelTest._columns[1:3], ModelTest)

    caplog.clear()
    with pytest.raises(orm_meta.NonexistentColumnError) as ex:
        postgres_orm._validate_cols([*ModelTest._columns[1:2], bad_cols[0]],
                ModelTest)
    assert 'Invalid column(s) for ModelTest:' in str(ex.value)
    assert caplog.record_tuples == [
        ('grand_trade_auto.orm.postgres_orm', logging.ERROR,
            "Invalid column(s) for ModelTest: `bad_col_1`"),
    ]

    caplog.clear()
    with pytest.raises(orm_meta.NonexistentColumnError) as ex:
        postgres_orm._validate_cols([*ModelTest._columns, *bad_cols], ModelTest)
    assert 'Invalid column(s) for ModelTest:' in str(ex.value)
    assert caplog.record_tuples[0][0] == 'grand_trade_auto.orm.postgres_orm'
    assert caplog.record_tuples[0][1] == logging.ERROR
    # Since code under test uses set, order varies -- must compare as set
    msg_parts = caplog.record_tuples[0][2].split(': ', 1)
    assert msg_parts[0] == 'Invalid column(s) for ModelTest'
    assert set(msg_parts[1].split(', ')) == {f'`{c}`' for c in bad_cols}



def test__prep_sanitized_vars():
    """
    Tests the `_prep_sanitized_vars()` method in `postgres_orm`.
    """
    data = {
        'col_1': 'val_1',
        'col_2': 'val_2',
        'col_3': 'val_3',
    }

    val_vars = postgres_orm._prep_sanitized_vars('', data)
    for i, (k, v) in enumerate(val_vars.items()):
        assert k == f'val{i}'
        assert v == data[list(data.keys())[i]]


    val_vars = postgres_orm._prep_sanitized_vars('test',
            dict(itertools.islice(data.items(), 1)))
    for i, (k, v) in enumerate(val_vars.items()):
        assert k == f'testval{i}'
        assert v == data[list(data.keys())[i]]

    val_vars = postgres_orm._prep_sanitized_vars('empty', {})
    assert val_vars == {}



def test__build_var_list_str():
    """
    Tests the `_build_var_list_str()` method in `postgres_orm`.
    """
    names = [
        'var_1',
        'var_2',
        'var_3',
    ]

    var_str = postgres_orm._build_var_list_str(names)
    assert var_str == '%(var_1)s, %(var_2)s, %(var_3)s'

    var_str = postgres_orm._build_var_list_str(names[:1])
    assert var_str == '%(var_1)s'

    var_str = postgres_orm._build_var_list_str([])
    assert var_str == ''



def test__build_col_var_list_str():
    """
    Tests the `_build_col_var_list_str()` method in `postgres_orm`.
    """
    col_names = [
        'col_1',
        'col_2',
        'col_3',
    ]
    var_names = [
        'var_1',
        'var_2',
        'var_3',
    ]

    cv_str = postgres_orm._build_col_var_list_str(col_names, var_names)
    assert cv_str == 'col_1 = %(var_1)s, col_2 = %(var_2)s, col_3 = %(var_3)s'

    cv_str = postgres_orm._build_col_var_list_str(col_names[:1], var_names[:1])
    assert cv_str == 'col_1 = %(var_1)s'

    cv_str = postgres_orm._build_col_var_list_str([], [])
    assert cv_str == ''

    with pytest.raises(AssertionError) as ex:
        postgres_orm._build_col_var_list_str([], [1])
    assert 'Col and vars must be same length!' == str(ex.value)



def test__build_where(caplog):
    """
    Tests the `_build_where()` method in `postgres_orm`.
    """
    caplog.set_level(logging.WARNING)

    # Ensure empty where should be empty
    assert postgres_orm._build_where(None) == ('', {})

    # Ensure single where clause works without col check
    where_single = ('col_1', model_meta.LogicOp.EQ, 'val_1')
    clause, vals = postgres_orm._build_where(where_single)
    assert clause == 'col_1 = %(wval0)s'
    assert vals == {'wval0': 'val_1'}

    # Ensure single where clause works with col check
    where_single = ('id', model_meta.LogicOp.EQ, 2)
    clause, vals = postgres_orm._build_where(where_single, ModelTest)
    assert clause == 'id = %(wval0)s'
    assert vals == {'wval0': 2}

    # Ensure single where clause fails with col check
    caplog.clear()
    where_single = ('bad_col', model_meta.LogicOp.EQ, 3)
    with pytest.raises(orm_meta.NonexistentColumnError) as ex:
        postgres_orm._build_where(where_single, ModelTest)
    assert 'Invalid column(s) for ModelTest:' in str(ex.value)
    assert caplog.record_tuples == [
        ('grand_trade_auto.orm.postgres_orm', logging.ERROR,
            "Invalid column(s) for ModelTest: `bad_col`"),
    ]

    # Ensure simply combo where clause works without col check
    where_combo = {
        model_meta.LogicCombo.AND: [
            ('col_1', model_meta.LogicOp.EQ, 'val_4'),
            ('col_2', model_meta.LogicOp.EQ, 5),
        ],
    }
    clause, vals = postgres_orm._build_where(where_combo)
    assert clause == '(col_1 = %(wval0)s AND col_2 = %(wval1)s)'
    assert vals == {'wval0': 'val_4', 'wval1': 5}

    # Ensure complex combo where clause works with col check
    where_combo = {
        model_meta.LogicCombo.AND: [
            ('col_1', model_meta.LogicOp.EQ, 'val_6'),
            {
                model_meta.LogicCombo.OR: [
                    ('col_2', model_meta.LogicOp.EQ, 7),
                    ('col_3', model_meta.LogicOp.EQ, 8),
                    {
                        model_meta.LogicCombo.AND: [
                            ('col_4', model_meta.LogicOp.EQ, 9),
                            ('col_5', model_meta.LogicOp.EQ, 10),
                            ('col_6', model_meta.LogicOp.EQ, 11),
                        ],
                    },
                ],
            },
            ('col_7', model_meta.LogicOp.EQ, 12),
        ],
    }
    clause, vals = postgres_orm._build_where(where_combo)
    assert clause == '(col_1 = %(wval0)s AND (col_2 = %(wval1)s' \
            + ' OR col_3 = %(wval2)s OR (col_4 = %(wval3)s' \
            + ' AND col_5 = %(wval4)s AND col_6 = %(wval5)s)) AND' \
            + ' col_7 = %(wval6)s)'
    assert vals == {
        'wval0': 'val_6',
        'wval1': 7,
        'wval2': 8,
        'wval3': 9,
        'wval4': 10,
        'wval5': 11,
        'wval6': 12,
    }

    # Ensure combo where clause fails with col check
    caplog.clear()
    where_combo = {
        model_meta.LogicCombo.AND: [
            ('id', model_meta.LogicOp.EQ, 'val_12'),
            ('bad_col', model_meta.LogicOp.EQ, 13),
        ],
    }
    with pytest.raises(orm_meta.NonexistentColumnError) as ex:
        postgres_orm._build_where(where_combo, ModelTest)
    assert 'Invalid column(s) for ModelTest:' in str(ex.value)
    assert caplog.record_tuples == [
        ('grand_trade_auto.orm.postgres_orm', logging.ERROR,
            "Invalid column(s) for ModelTest: `bad_col`"),
    ]

    # Ensure combo where clause fails with any value error
    caplog.clear()
    where_combo = {
        'not a combo': [
            ('col_1', 'not an op', 'val_14'),
            ('col_2', model_meta.LogicOp.EQ, 15),
        ],
    }
    with pytest.raises(ValueError) as ex:
        postgres_orm._build_where(where_combo)
    assert 'Invalid or Unsupported Logic Op: not an op' in str(ex.value)
    assert caplog.record_tuples == [
        ('grand_trade_auto.orm.postgres_orm', logging.ERROR,
            "Invalid or Unsupported Logic Op: not an op"),
    ]



def test__build_conditional_combo(caplog):
    """
    Tests the `_build_conditional_combo()` method in `postgres_orm`.
    """
    caplog.set_level(logging.WARNING)

    # Ensure simply combo where clause works without col check
    where_conds = [
        ('col_1', model_meta.LogicOp.EQ, 'val_1'),
        ('col_2', model_meta.LogicOp.EQ, 2),
    ]
    vals = {}
    clause = postgres_orm._build_conditional_combo(model_meta.LogicCombo.AND,
            where_conds, vals)
    assert clause == '(col_1 = %(wval0)s AND col_2 = %(wval1)s)'
    assert vals == {'wval0': 'val_1', 'wval1': 2}

    # Ensure nested combo where clause works with col check
    vals = {'existing_item': 'ex_val'}
    where_conds = [
            ('id', model_meta.LogicOp.EQ, 'val_3'),
            {
                model_meta.LogicCombo.AND: [
                    ('int_data', model_meta.LogicOp.EQ, 4),
                    ('bool_data', model_meta.LogicOp.EQ, 5),
                ],
            },
    ]
    clause = postgres_orm._build_conditional_combo(
            model_meta.LogicCombo.OR, where_conds, vals, ModelTest)
    assert clause == '(id = %(wval1)s OR (int_data = %(wval2)s' \
            + ' AND bool_data = %(wval3)s))'
    assert vals == {
        'existing_item': 'ex_val',
        'wval1': 'val_3',
        'wval2': 4,
        'wval3': 5,
    }

    # Ensure fails with bad col
    caplog.clear()
    where_conds = [
        ('bad_col', model_meta.LogicOp.EQ, 'val_6'),
        ('col_2', model_meta.LogicOp.EQ, 7),
    ]
    with pytest.raises(orm_meta.NonexistentColumnError) as ex:
        postgres_orm._build_conditional_combo(
            model_meta.LogicCombo.OR, where_conds, {}, ModelTest)
    assert 'Invalid column(s) for ModelTest:' in str(ex.value)
    assert caplog.record_tuples == [
        ('grand_trade_auto.orm.postgres_orm', logging.ERROR,
            "Invalid column(s) for ModelTest: `bad_col`"),
    ]

    # Ensure fails with bad combo
    caplog.clear()
    with pytest.raises(ValueError) as ex:
        postgres_orm._build_conditional_combo('bad combo', [], {})
    assert 'Invalid or Unsupported Logic Combo:' in str(ex.value)
    assert caplog.record_tuples == [
        ('grand_trade_auto.orm.postgres_orm', logging.ERROR,
            "Invalid or Unsupported Logic Combo: bad combo"),
    ]



def test__build_conditional_single(caplog):
    """
    Tests the `_build_conditional_single()` method in `postgres_orm`.
    """
    #pylint: disable=too-many-statements

    caplog.set_level(logging.WARNING)

    # Ensure all supported ops work as expected
    vals = {}
    clause = postgres_orm._build_conditional_single(
            ('col_1', model_meta.LogicOp.NOT_NULL), vals)
    assert clause == 'col_1 NOT NULL'
    assert vals == {}

    vals = {}
    clause = postgres_orm._build_conditional_single(
            ('col_2', model_meta.LogicOp.EQ, 2), vals)
    assert clause == 'col_2 = %(wval0)s'
    assert vals == {'wval0': 2}

    vals = {}
    clause = postgres_orm._build_conditional_single(
            ('col_3', model_meta.LogicOp.EQUAL, 3), vals)
    assert clause == 'col_3 = %(wval0)s'
    assert vals == {'wval0': 3}

    vals = {}
    clause = postgres_orm._build_conditional_single(
            ('col_4', model_meta.LogicOp.EQUALS, 4), vals)
    assert clause == 'col_4 = %(wval0)s'
    assert vals == {'wval0': 4}

    vals = {}
    clause = postgres_orm._build_conditional_single(
            ('col_5', model_meta.LogicOp.LT, 5), vals)
    assert clause == 'col_5 < %(wval0)s'
    assert vals == {'wval0': 5}

    vals = {}
    clause = postgres_orm._build_conditional_single(
            ('col_6', model_meta.LogicOp.LESS_THAN, 6), vals)
    assert clause == 'col_6 < %(wval0)s'
    assert vals == {'wval0': 6}

    vals = {}
    clause = postgres_orm._build_conditional_single(
            ('col_7', model_meta.LogicOp.LTE, 7), vals)
    assert clause == 'col_7 <= %(wval0)s'
    assert vals == {'wval0': 7}

    vals = {}
    clause = postgres_orm._build_conditional_single(
            ('col_8', model_meta.LogicOp.LESS_THAN_OR_EQUAL, 8), vals)
    assert clause == 'col_8 <= %(wval0)s'
    assert vals == {'wval0': 8}

    vals = {}
    clause = postgres_orm._build_conditional_single(
            ('col_9', model_meta.LogicOp.GT, 9), vals)
    assert clause == 'col_9 > %(wval0)s'
    assert vals == {'wval0': 9}

    vals = {}
    clause = postgres_orm._build_conditional_single(
            ('col_10', model_meta.LogicOp.GREATER_THAN, 10), vals)
    assert clause == 'col_10 > %(wval0)s'
    assert vals == {'wval0': 10}

    vals = {}
    clause = postgres_orm._build_conditional_single(
            ('col_11', model_meta.LogicOp.GTE, 11), vals)
    assert clause == 'col_11 >= %(wval0)s'
    assert vals == {'wval0': 11}

    vals = {}
    clause = postgres_orm._build_conditional_single(
            ('col_12', model_meta.LogicOp.GREATER_THAN_OR_EQUAL, 12), vals)
    assert clause == 'col_12 >= %(wval0)s'
    assert vals == {'wval0': 12}

    # Ensure no issue providing 3 cond's when 2 expected and with vars
    vals = {'existing_col': 'ex_val'}
    clause = postgres_orm._build_conditional_single(
            ('col_13', model_meta.LogicOp.NOT_NULL, 'no_val'), vals)
    assert clause == 'col_13 NOT NULL'
    assert vals == {'existing_col': 'ex_val'}

    # Ensure works with existing values
    vals = {'existing_col': 'ex_val'}
    clause = postgres_orm._build_conditional_single(
            ('col_14', model_meta.LogicOp.EQ, 14), vals)
    assert clause == 'col_14 = %(wval1)s'
    assert vals == {'existing_col': 'ex_val', 'wval1': 14}

    # Ensure works with col valid
    vals = {}
    clause = postgres_orm._build_conditional_single(
            ('id', model_meta.LogicOp.EQ, 15), vals, ModelTest)
    assert clause == 'id = %(wval0)s'
    assert vals == {'wval0': 15}

    # Ensure bad col caught
    caplog.clear()
    with pytest.raises(orm_meta.NonexistentColumnError) as ex:
        postgres_orm._build_conditional_single(
            ('bad_col', model_meta.LogicOp.EQ, 16), {}, ModelTest)
    assert 'Invalid column(s) for ModelTest:' in str(ex.value)
    assert caplog.record_tuples == [
        ('grand_trade_auto.orm.postgres_orm', logging.ERROR,
            "Invalid column(s) for ModelTest: `bad_col`"),
    ]

    # Ensure bad op caught
    caplog.clear()
    with pytest.raises(ValueError) as ex:
        postgres_orm._build_conditional_single(('col_17', 'bad op'), {})
    assert 'Invalid or Unsupported Logic Op: bad op' in str(ex.value)
    assert caplog.record_tuples == [
        ('grand_trade_auto.orm.postgres_orm', logging.ERROR,
            "Invalid or Unsupported Logic Op: bad op"),
    ]



def test__build_and_validate_order(caplog):
    """
    Tests the `_build_and_validate_order()` method in `postgres_orm`.
    """
    caplog.set_level(logging.WARNING)

    # Ensure empty order works
    assert postgres_orm._build_and_validate_order(None) == ''

    # Ensure single order works
    order_simple = [('col_1', model_meta.SortOrder.ASC)]
    clause = postgres_orm._build_and_validate_order(order_simple)
    assert clause == 'ORDER BY col_1 ASC'

    # Ensure multiple order works
    order_complex = [
        ('col_1', model_meta.SortOrder.DESC),
        ('col_2', model_meta.SortOrder.ASC),
    ]
    clause = postgres_orm._build_and_validate_order(order_complex)
    assert clause == 'ORDER BY col_1 DESC, col_2 ASC'

    # Ensure column validation works
    order_simple = [('id', model_meta.SortOrder.ASC)]
    clause = postgres_orm._build_and_validate_order(order_simple, ModelTest)
    assert clause == 'ORDER BY id ASC'

    # Ensure column validation fails with bad col
    caplog.clear()
    order_complex = [
        ('id', model_meta.SortOrder.DESC),
        ('bad_col', model_meta.SortOrder.ASC),
    ]
    with pytest.raises(orm_meta.NonexistentColumnError) as ex:
        postgres_orm._build_and_validate_order(order_complex, ModelTest)
    assert 'Invalid column(s) for ModelTest:' in str(ex.value)
    assert caplog.record_tuples == [
        ('grand_trade_auto.orm.postgres_orm', logging.ERROR,
            'Invalid column(s) for ModelTest: `bad_col`'),
    ]

    # Ensure bad sort order fails
    caplog.clear()
    order_simple = [('col_1', 'bad order')]
    with pytest.raises(ValueError) as ex:
        postgres_orm._build_and_validate_order(order_simple)
    assert 'Invalid or Unsupported Sort Order:' in str(ex.value)
    assert caplog.record_tuples == [
        ('grand_trade_auto.orm.postgres_orm', logging.ERROR,
            'Invalid or Unsupported Sort Order: bad order'),
        ('grand_trade_auto.orm.postgres_orm', logging.ERROR,
            'Failed to parse sort order:'
            + ' Invalid or Unsupported Sort Order: bad order'),
    ]

    # Ensure bad order format fails
    caplog.clear()
    order_bad = [('col_1', model_meta.SortOrder.ASC, 'bad extra')]
    with pytest.raises(ValueError) as ex:
        postgres_orm._build_and_validate_order(order_bad)
    assert 'Failed to parse sort order: ' in str(ex.value)
    assert caplog.record_tuples == [
        ('grand_trade_auto.orm.postgres_orm', logging.ERROR,
            'Failed to parse sort order:'
            + ' too many values to unpack (expected 2)'),
    ]



def test__build_and_validate_limit(caplog):
    """
    Tests the `_build_and_validate_limti()` method in `postgres_orm`.
    """
    caplog.set_level(logging.WARNING)

    # Ensure empty limit works
    assert postgres_orm._build_and_validate_limit(None) == ''

    # Ensure integer limit works
    assert postgres_orm._build_and_validate_limit(123) == 'LIMIT 123'

    # Ensure non-integer fails
    caplog.clear()
    with pytest.raises(ValueError) as ex:
        postgres_orm._build_and_validate_limit('not an int')
    assert 'Failed to parse limit, likely not a number:' in str(ex.value)
    assert caplog.record_tuples == [
        ('grand_trade_auto.orm.postgres_orm', logging.ERROR,
            "Failed to parse limit, likely not a number:"
            + " invalid literal for int() with base 10: 'not an int'"),
    ]
