#!/usr/bin/env python3
"""
Tests the grand_trade_auto.model.model_meta functionality.

Per [pytest](https://docs.pytest.org/en/reorganize-docs/new-docs/user/naming_conventions.html),
all tiles, classes, and methods will be prefaced with `test_/Test` to comply
with auto-discovery (others may exist, but will not be part of test suite
directly).

Module Attributes:
  logger (Logger): Logger for this module.

(C) Copyright 2021 Jonathan Casey.  All Rights Reserved Worldwide.
"""
#pylint: disable=protected-access  # Allow for purpose of testing those elements
#pylint: disable=use-implicit-booleaness-not-comparison
#   +-> want to specifically check type in most tests -- `None` is a fail

import copy
import logging

import pandas as pd
import psycopg2.errors
import pytest

from grand_trade_auto.model import model_meta
from grand_trade_auto.orm import orm_meta



logger = logging.getLogger(__name__)



def test_enum_currency():
    """
    Tests the essential items of the `Currency` Enum in `model_meta`.
    """
    # Must test enum values since these are set in the database schema
    assert model_meta.Currency('usd') == model_meta.Currency.USD
    # Failing length here likely means new values added -- just add above
    assert len(model_meta.Currency) == 1



def test_enum_market():
    """
    Tests the essential items of the `Market` Enum in `model_meta`.
    """
    # Must test enum values since these are set in the database schema
    assert model_meta.Market('crypto') == model_meta.Market.CRYPTO
    assert model_meta.Market('forex') == model_meta.Market.FOREX
    assert model_meta.Market('futures') == model_meta.Market.FUTURES
    assert model_meta.Market('stock') == model_meta.Market.STOCK
    # Failing length here likely means new values added -- just add above
    assert len(model_meta.Market) == 4



def test_enum_price_frequency():
    """
    Tests the essential items of the `PriceFrequency` Enum in `model_meta`.
    """
    # Must test enum values since these are set in the database schema
    assert model_meta.PriceFrequency('1min') == model_meta.PriceFrequency.MIN_1
    assert model_meta.PriceFrequency('5min') == model_meta.PriceFrequency.MIN_5
    assert model_meta.PriceFrequency('10min') \
            == model_meta.PriceFrequency.MIN_10
    assert model_meta.PriceFrequency('15min') \
            == model_meta.PriceFrequency.MIN_15
    assert model_meta.PriceFrequency('30min') \
            == model_meta.PriceFrequency.MIN_30
    assert model_meta.PriceFrequency('hourly') \
            == model_meta.PriceFrequency.HOURLY
    assert model_meta.PriceFrequency('daily') \
            == model_meta.PriceFrequency.DAILY
    # Failing length here likely means new values added -- just add above
    assert len(model_meta.PriceFrequency) == 7



def test_enum_logic_combo():
    """
    Tests the essential items of the `LogicCombo` Enum in `model_meta`.
    """
    # Do not need to test values since access by value unsupported
    names = {'AND', 'OR'}
    assert names == {e.name for e in list(model_meta.LogicCombo)}



def test_enum_logic_op():
    """
    Tests the essential items of the `LogicOp` Enum in `model_meta`.
    """
    # Do not need to test values since access by value unsupported
    names = {'EQUAL', 'EQUALS', 'EQ', 'LESS_THAN', 'LT',
            'LESS_THAN_OR_EQUAL', 'LTE', 'GREATER_THAN', 'GT',
            'GREATER_THAN_OR_EQUAL', 'GTE', 'NOT_NULL'}
    assert names == {e.name for e in list(model_meta.LogicOp)}



def test_enum_return_as():
    """
    Tests the essential items of the `ReturnAs` Enum in `model_meta`.
    """
    # Must test enum values since this allows access by value
    assert model_meta.ReturnAs('model') == model_meta.ReturnAs.MODEL
    assert model_meta.ReturnAs('pandas') == model_meta.ReturnAs.PANDAS
    assert len(model_meta.ReturnAs) == 2



def test_enum_sort_order():
    """
    Tests the essential items of the `SortOrder` Enum in `model_meta`.
    """
    # Do not need to test values since access by value unsupported
    names = {'ASC', 'DESC'}
    assert names == {e.name for e in list(model_meta.SortOrder)}



class ModelTest(model_meta.Model):
    """
    A test model to use for testing within this module.
    """
    _table_name = 'test_model_meta'

    _columns = (
        'id',
        'col_1',
        'col_2',
        'col_auto_ro',
    )

    _read_only_columns = (
        'col_auto_ro',
    )

    # Column Attributes -- MUST match _columns!
    # id defined in super
    col_1 = None
    col_2 = None
    col_auto_ro = None
    # End of Column Attributes



    def __copy__(self):
        """
        Return an effective shallow copy for these testing purposes.
        """
        shallow_copy = ModelTest(self._orm)
        for attr in ['id', 'col_1', 'col_2', 'col_auto_ro']:
            setattr(shallow_copy, attr, getattr(self, attr))
        return shallow_copy



class OrmTest(orm_meta.Orm):
    """
    A barebones Orm that can be used for most tests.

    Instance Attributes:
      _mock_db_results ([]): A list of objects that would be in the database if
        there were a db.  Meant to store results for add() so they can be
        checked later, etc.
    """
    def __init__(self, db):
        """
        Add the `_mock_db_results` instance attribute.
        """
        super().__init__(db)
        self._mock_db_results = []



    def _create_schema_enum_currency(self):
        """
        Not needed / will not be used.
        """

    def _create_schema_enum_market(self):
        """
        Not needed / will not be used.
        """

    def _create_schema_enum_price_frequency(self):
        """
        Not needed / will not be used.
        """

    def _create_schema_table_company(self):
        """
        Not needed / will not be used.
        """

    def _create_schema_table_datafeed_src(self):
        """
        Not needed / will not be used.
        """

    def _create_schema_table_exchange(self):
        """
        Not needed / will not be used.
        """

    def _create_schema_table_security(self):
        """
        Not needed / will not be used.
        """

    def _create_schema_table_security_price(self):
        """
        Not needed / will not be used.
        """

    def _create_schema_table_stock_adjustment(self):
        """
        Not needed / will not be used.
        """



    def add(self, model_cls, data, **kwargs):
        """
        Fake adding something to mock results, and check cols.  Expected to
        check afterwards.

        Raises:
          (psycopg2.errors.GeneratedAlways): Raised as a simulated error if
            attempting to update a read only column.  This should be triggered
            and tested as part of a test.
          [Pass through expected]
        """
        OrmTest._validate_cols(data.keys(), model_cls)
        if any(c in data for c in model_cls._read_only_columns):
            raise psycopg2.errors.GeneratedAlways(   # pylint: disable=no-member
                    '...can only be updated to DEFAULT')

        res = {
            'model': model_cls(self, data),
            'extra_args': kwargs,
        }
        self._mock_db_results.append(res)



    def update(self, model_cls, data, where, **kwargs):
        """
        Fake updating something in mock results, and check cols.  Expected to
        have existing data.  Limited 'where' clause support.

        Raises:
          (psycopg2.errors.GeneratedAlways): Raised as a simulated error if
            attempting to update a read only column.  This should be triggered
            and tested as part of a test.
          (ValueError): Raised if an unsupported LogicOp is provided.  This has
            much more limited support for LogicOps to limit how much needs to be
            implemented here.  If this is raised, the test should be redesigned
            to avoid it rather than catching it.
          [Pass through expected]
        """
        OrmTest._validate_cols(data.keys(), model_cls)
        if where[1] is not model_meta.LogicOp.EQUALS:
            raise ValueError('Test Error: Provided LogicOp not supported')
        if any(c in data for c in model_cls._read_only_columns):
            raise psycopg2.errors.GeneratedAlways(   # pylint: disable=no-member
                    '...can only be updated to DEFAULT')

        for res in self._mock_db_results:
            if getattr(res['model'], where[0]) == where[2]:
                for k, v in data.items():
                    setattr(res['model'], k, v)
                # Intentionally override extra_args to be able to test
                res['extra_args'] = kwargs



    def delete(self, model_cls, where, really_delete_all=False, **kwargs):
        """
        Fake deleting something in mock results, and check cols.  Expected to
        have existing data.  Limited 'where' clause support.

        Raises:
          (ValueError):
            [with respect to LogicOp] Raised if an unsupported LogicOp is
              provided.  This has much more limited support for LogicOps to
              limit how much needs to be implemented here.  If this is raised,
              the test should be redesigned to avoid it rather than catching it.
            [with respect to really_delete_all] Raised as a simulated error if
              the where clause is empty but `really_delete_all` was not set to
              True.  This should be triggered and tested as part of a test.
        """
        if where and where[1] is not model_meta.LogicOp.EQUALS:
            raise ValueError('Test Error: Provided LogicOp not supported')
        if not where and really_delete_all:
            self._mock_db_results = []
            return
        if not where:
            raise ValueError('Need to confirm w/ really_delete_all')

        for res in self._mock_db_results:
            if getattr(res['model'], where[0]) == where[2]:
                del res['model']
                # Intentionally override extra_args to be able to test
                res['extra_args'] = kwargs



    def query(self, model_cls, return_as, columns_to_return=None,
            where=None, limit=None, order=None, **kwargs):
        """
        Fake querying something from mock results, and check cols.  Expected to
        have existing data.  Limited 'where' and 'order' clause support.

        Raises:
          (psycopg2.errors.GeneratedAlways): Raised as a simulated error if
            attempting to update a read only column.  This should be triggered
            and tested as part of a test.
          (ValueError): Raised if an unsupported LogicOp, SortOrder, or ReturnAs
            is provided.  This has much more limited support for LogicOps,
            SortOrders, and ReturnAs options to limit how much needs to be
            implemented here.  If this is raised, the test should be redesigned
            to avoid it rather than catching it.
          [Pass through expected]
        """
        #pylint: disable=too-many-branches
        if columns_to_return is not None:
            OrmTest._validate_cols(columns_to_return, model_cls)
        if where and where[1] is not model_meta.LogicOp.EQUALS:
            raise ValueError('Test Error: Provided LogicOp not supported')
        if order and order[1] is not model_meta.SortOrder.DESC:
            raise ValueError('Test Error: Provided SortOrder not supported')

        cols_to_omit = []
        if columns_to_return:
            for col in ModelTest._columns:
                if col not in columns_to_return:
                    cols_to_omit.append(col)

        results = []
        for res in self._mock_db_results:
            if not where or getattr(res['model'], where[0]) == where[2]:
                # Intentionally override extra_args to be able to test
                res_copy = {
                    'model': copy.copy(res['model']),
                    'extra_args': kwargs,
                }
                for col in cols_to_omit:
                    setattr(res_copy['model'], col, None)
                results.append(res_copy)

        if order:
            # Hard-coded to only support DESC, hence reverse is True
            results.sort(key=lambda mdl: getattr(mdl['model'], order[0]),
                    reverse=True)

        if limit is not None and limit < len(results):
            results = results[:limit]

        if model_meta.ReturnAs(return_as) is model_meta.ReturnAs.MODEL:
            return [r['model'] for r in results]
        if model_meta.ReturnAs(return_as) is model_meta.ReturnAs.PANDAS:
            # Flatten 'model' level of dict for pd.df import
            mdl_cols = columns_to_return or ModelTest._columns
            for res in results:
                for col in mdl_cols:
                    res[col] = getattr(res['model'], col)
                del res['model']
            return pd.DataFrame(results)
        raise ValueError('Test Error: Provided ReturnAs not supported')



    @staticmethod
    def _validate_cols(cols, model_cls):
        """
        A helper method just for this testing to check columns, raise an
        exception if there is an issue.

        Raises:
          (NonexistentColumnError): Raised as a simulated error if at least one
            column provided is not in the list of columns for the provided
            model.  This should be triggered and tested as part of a test.
        """
        valid_cols = model_cls.get_columns()
        if not set(cols).issubset(valid_cols):
            err_msg = f'Invalid column(s) for {model_cls.__name__}:'
            err_msg += f' `{"`, `".join(set(cols) - set(valid_cols))}`'
            logger.error(err_msg)
            raise orm_meta.NonexistentColumnError(err_msg)



def test_model_init(caplog):
    """
    Tests the `__init__()` method in `Model`.
    """
    caplog.set_level(logging.WARNING)

    # Ensure bare minimum init works
    model = ModelTest('test_orm')
    assert model._orm == 'test_orm'
    assert model._active_cols == set()
    for col in ModelTest._columns:
        assert getattr(model, col) is None

    # Ensure data stored properly with valid cols
    data = {'id': 1, 'col_2': 2}
    model = ModelTest('', data)
    assert model._orm == ''
    assert model._active_cols == set(data.keys())
    for col, val in data.items():
        assert getattr(model, col) == val
    for col in (set(ModelTest._columns) - set(data.keys())):
        assert getattr(model, col) is None

    # Ensure invalid col fails
    caplog.clear()
    data = {'id': 3, 'bad_col': 4}
    with pytest.raises(AttributeError) as ex:
        ModelTest('', data)
    assert 'Invalid data column for ModelTest: bad_col' in str(ex.value)
    assert caplog.record_tuples == [
        ('grand_trade_auto.model.model_meta', logging.ERROR,
            'Invalid data column for ModelTest: bad_col'),
    ]



def test_model_setattr(caplog):
    """
    Tests the `__setattr__()` method in `Model`.
    """
    caplog.set_level(logging.WARNING)

    model = ModelTest('')
    assert model._active_cols == set()

    model.id = 1
    assert model._active_cols == set(['id'])
    assert model.id == 1

    model._table_name = 'not active col'
    assert model._active_cols == set(['id'])
    assert model._table_name == 'not active col'

    caplog.clear()
    assert model.col_auto_ro is None
    assert set(model._read_only_columns) == set(['col_auto_ro'])
    model.col_auto_ro = '1st setting'
    assert model.col_auto_ro == '1st setting'
    with pytest.raises(AttributeError) as ex:
        model.col_auto_ro = '2nd setting'
    assert 'Cannot set a non-None read-only column more than' in str(ex.value)
    assert caplog.record_tuples == [
        ('grand_trade_auto.model.model_meta', logging.ERROR,
            'Cannot set a non-None read-only column more than once:'
            + ' ModelTest.col_auto_ro'),
    ]
    assert model.col_auto_ro == '1st setting'



def test_get_table_name():
    """
    Tests the `get_table_name()` method in `Model`.
    """
    model = ModelTest('')
    model._table_name = 'different name'
    assert ModelTest.get_table_name() == 'test_model_meta'
    assert model.get_table_name() == 'test_model_meta'



def test_get_columns():
    """
    Tests the `get_columns()` method in `Model`.
    """
    model = ModelTest('')
    model._columns = ('wrong col', 'fake_col')
    assert ModelTest.get_columns() == ('id', 'col_1', 'col_2', 'col_auto_ro')
    assert model.get_columns() == ('id', 'col_1', 'col_2', 'col_auto_ro')



def test_add_and_direct(caplog, monkeypatch):
    """
    Tests the `add()` and `add_direct()` methods in `Model`.
    """
    caplog.set_level(logging.WARNING)

    orm = OrmTest(None)
    assert orm._mock_db_results == []

    data_1 = {
        'col_1': 1,
        'col_2': 2,
    }
    ModelTest.add_direct(orm, data_1, conn='fake_conn')
    assert len(orm._mock_db_results) == 1
    res = orm._mock_db_results[0]
    assert res['model'].id is None
    assert res['model'].col_1 == 1
    assert res['model'].col_2 == 2
    assert res['extra_args'] == {'conn': 'fake_conn'}

    data_2 = {
        'col_1': 3,
        'col_2': 4,
    }
    model = ModelTest(orm, data_2)
    model._active_cols.remove('col_1')
    model.add(cursor='fake_cursor', conn=4)
    assert len(orm._mock_db_results) == 2
    res = orm._mock_db_results[1]
    assert res['model'].id is None
    assert res['model'].col_1 is None   # Removed from active, should be skipped
    assert res['model'].col_2 == 4
    assert res['extra_args'] == {'cursor': 'fake_cursor', 'conn': 4}

    data_3 = {
        'col_1': 5,
        'col_auto_ro': 'should fail direct',
    }
    model = ModelTest(orm, data_3)
    model.add()
    last_model = orm._mock_db_results[-1]['model']
    assert last_model.col_1 == model.col_1
    assert last_model.col_auto_ro is None
    assert model.col_auto_ro == 'should fail direct'
    with pytest.raises(
            psycopg2.errors.GeneratedAlways) as ex:  # pylint: disable=no-member
        ModelTest.add_direct(orm, data_3)
    assert '...can only be updated to DEFAULT' in str(ex.value)

    caplog.clear()
    with pytest.raises(orm_meta.NonexistentColumnError) as ex:
        ModelTest.add_direct(orm, {'bad_col': 6})
    assert 'Invalid column(s) for ModelTest: `bad_col`' in str(ex.value)
    assert caplog.record_tuples == [
        ('tests.unit.model.test_model_meta', logging.ERROR,
            'Invalid column(s) for ModelTest: `bad_col`')
    ]

    def mock_get_active_data_as_dict(self):
        """
        Injects a bad col on purpose.
        """
        cols = {c: getattr(self, c) for c in self._active_cols}
        cols['bad_col'] = 7
        return cols

    caplog.clear()
    monkeypatch.setattr(ModelTest, '_get_active_data_as_dict',
            mock_get_active_data_as_dict)
    data_4 = {
        'col_1': 8,
    }
    model = ModelTest(orm, data_4)
    with pytest.raises(orm_meta.NonexistentColumnError) as ex:
        model.add()
    assert 'Invalid column(s) for ModelTest: `bad_col`' in str(ex.value)
    assert caplog.record_tuples == [
        ('tests.unit.model.test_model_meta', logging.ERROR,
            'Invalid column(s) for ModelTest: `bad_col`')
    ]



def test_update_and_direct(caplog, monkeypatch):
    """
    Tests the `update()` and `udpate_direct()` methods in `Model`.
    """
    #pylint: disable=too-many-locals, too-many-statements
    caplog.set_level(logging.WARNING)

    data_orig = [
        {
            'col_1': 1,
            'col_2': 2,
        },
        {
            'col_1': 3,
            'col_2': 2,
        },
    ]

    orm = OrmTest(None)
    for i, data in enumerate(data_orig):
        orm.add(ModelTest, data, fake_count=i)
    assert len(orm._mock_db_results) == 2
    assert orm._mock_db_results[0]['model'].col_1 == 1
    assert orm._mock_db_results[1]['model'].col_1 == 3
    assert orm._mock_db_results[1]['extra_args'] == {'fake_count': 1}

    new_data_1 = {
        'id': 4,
        'col_1': 5,
    }
    where_1 = ('col_1', model_meta.LogicOp.EQUALS, 1)
    ModelTest.update_direct(orm, new_data_1, where_1, new_fake=True)
    assert len(orm._mock_db_results) == 2
    res_1 = orm._mock_db_results[0]
    res_2 = orm._mock_db_results[1]
    assert res_1['model'].id == 4
    assert res_1['model'].col_1 == 5
    assert res_1['model'].col_2 == 2
    assert res_1['extra_args'] == {'new_fake': True}
    assert res_2['model'].id is None
    assert res_2['model'].col_1 == 3
    assert res_2['model'].col_2 == 2
    assert res_2['extra_args'] == {'fake_count': 1}

    new_data_2 = {
        'col_1': 6,
    }
    where_2 = ('col_2', model_meta.LogicOp.EQUALS, 2)
    ModelTest.update_direct(orm, new_data_2, where_2, new_new_fake='yes')
    assert len(orm._mock_db_results) == 2
    res_1 = orm._mock_db_results[0]
    res_2 = orm._mock_db_results[1]
    assert res_1['model'].id == 4
    assert res_1['model'].col_1 == 6
    assert res_1['model'].col_2 == 2
    assert res_1['extra_args'] == {'new_new_fake': 'yes'}
    assert res_2['model'].id is None
    assert res_2['model'].col_1 == 6
    assert res_2['model'].col_2 == 2
    assert res_2['extra_args'] == {'new_new_fake': 'yes'}

    with pytest.raises(
            psycopg2.errors.GeneratedAlways) as ex:  # pylint: disable=no-member
        ModelTest.update_direct(orm, {'col_auto_ro': 'fail'}, where_2)
    assert '...can only be updated to DEFAULT' in str(ex.value)

    # Create an effective semi-shallow copy of 1st db result...
    model_copy = copy.copy(orm._mock_db_results[0]['model'])
    # ...then try modifying the data...including ro col since unused so far...
    model_copy.col_1 = 7
    model_copy.col_2 = 8
    model_copy.col_auto_ro = 'allowed but ignored'
    # ...but act like one col not really active...
    model_copy._active_cols.remove('col_1')
    model_copy.update(another_fake=9)
    assert len(orm._mock_db_results) == 2
    res_1 = orm._mock_db_results[0]
    res_2 = orm._mock_db_results[1]
    assert res_1['model'].id == 4
    assert res_1['model'].col_1 == 6
    assert res_1['model'].col_2 == 8
    assert res_1['model'].col_auto_ro is None
    assert res_1['extra_args'] == {'another_fake': 9}
    assert res_2['model'].id is None
    assert res_2['model'].col_1 == 6
    assert res_2['model'].col_2 == 2
    assert res_2['extra_args'] == {'new_new_fake': 'yes'}
    assert model_copy.col_1 == 7
    assert model_copy.col_2 == 8

    caplog.clear()
    with pytest.raises(orm_meta.NonexistentColumnError) as ex:
        ModelTest.update_direct(orm, {'bad_col': 5}, None)
    assert 'Invalid column(s) for ModelTest: `bad_col`' in str(ex.value)
    assert caplog.record_tuples == [
        ('tests.unit.model.test_model_meta', logging.ERROR,
            'Invalid column(s) for ModelTest: `bad_col`')
    ]

    def mock_get_active_data_as_dict(self):
        """
        Injects a bad col on purpose.
        """
        cols = {c: getattr(self, c) for c in self._active_cols}
        cols['bad_col'] = 10
        return cols

    caplog.clear()
    monkeypatch.setattr(ModelTest, '_get_active_data_as_dict',
            mock_get_active_data_as_dict)
    data_3 = {
        'id': 11,
        'col_1': 12,
    }
    model = ModelTest(orm, data_3)
    with pytest.raises(orm_meta.NonexistentColumnError) as ex:
        model.update()
    assert 'Invalid column(s) for ModelTest: `bad_col`' in str(ex.value)
    assert caplog.record_tuples == [
        ('tests.unit.model.test_model_meta', logging.ERROR,
            'Invalid column(s) for ModelTest: `bad_col`')
    ]



def test_delete_and_direct():
    """
    Tests the `update()` and `udpate_direct()` methods in `Model`.
    """
    #pylint: disable=too-many-statements

    data_orig = [
        {
            'id': 1,
            'col_1': 2,
            'col_2': 3,
        },
        {
            'id': 4,
            'col_1': 5,
            'col_2': 3,
        },
    ]
    orm = OrmTest(None)

    def _clear_load_and_verify_init_data():
        """
        Clears the existing "db" data, loads the initial, and then verifies.
        """
        orm._mock_db_results = []
        for i, data in enumerate(data_orig):
            orm.add(ModelTest, data, fake_count=i)
        assert len(orm._mock_db_results) == 2
        assert orm._mock_db_results[0]['model'].id == 1
        assert orm._mock_db_results[0]['model'].col_1 == 2
        assert orm._mock_db_results[1]['model'].col_1 == 5
        assert orm._mock_db_results[1]['extra_args'] == {'fake_count': 1}

    _clear_load_and_verify_init_data()
    where_1 = ('col_1', model_meta.LogicOp.EQUALS, 2)
    ModelTest.delete_direct(orm, where_1, fake_arg=1)
    assert len(orm._mock_db_results) == 2
    res_1 = orm._mock_db_results[0]
    res_2 = orm._mock_db_results[1]
    assert 'model' not in res_1
    assert res_1['extra_args'] == {'fake_arg': 1}
    assert res_2['model'].id == 4
    assert res_2['model'].col_1 == 5
    assert res_2['model'].col_2 == 3
    assert res_2['extra_args'] == {'fake_count': 1}

    _clear_load_and_verify_init_data()
    where_2 = ('col_2', model_meta.LogicOp.EQUALS, 3)
    ModelTest.delete_direct(orm, where_2, fake_arg_again=2)
    assert len(orm._mock_db_results) == 2
    res_1 = orm._mock_db_results[0]
    res_2 = orm._mock_db_results[1]
    assert 'model' not in res_1
    assert res_1['extra_args'] == {'fake_arg_again': 2}
    assert 'model' not in res_2
    assert res_2['extra_args'] == {'fake_arg_again': 2}

    _clear_load_and_verify_init_data()
    with pytest.raises(ValueError) as ex:
        ModelTest.delete_direct(orm, None)
    assert 'Need to confirm w/ really_delete_all' in str(ex.value)

    ModelTest.delete_direct(orm, None, really_delete_all=True)
    assert orm._mock_db_results == []

    _clear_load_and_verify_init_data()
    # Create an effective semi-shallow copy of 1st db result...
    model_copy = copy.copy(orm._mock_db_results[0]['model'])
    # ...then try modifying the data...
    model_copy.col_1 = 6
    model_copy.delete(another_fake=True)
    assert len(orm._mock_db_results) == 2
    res_1 = orm._mock_db_results[0]
    res_2 = orm._mock_db_results[1]
    assert 'model' not in res_1
    assert res_1['extra_args'] == {'another_fake': True}
    assert res_2['model'].id == 4
    assert res_2['model'].col_1 == 5
    assert res_2['model'].col_2 == 3
    assert res_2['extra_args'] == {'fake_count': 1}



def test_query_direct(caplog):
    """
    Tests the `query_direct()` method in `Model`.
    """
    caplog.set_level(logging.WARNING)

    data_orig = [
        {
            'id': 1,
            'col_1': 2,
            'col_2': 3,
        },
        {
            'id': 4,
            'col_1': 1,
            'col_2': 3,
        },
        {
            'id': 5,
            'col_1': 2,
            'col_2': 3,
        },
        {
            'id': 3,
            'col_1': 2,
            'col_2': 3,
        },
    ]
    orm = OrmTest(None)
    for i, data in enumerate(data_orig):
        orm.add(ModelTest, data, fake_count=i)
    assert len(orm._mock_db_results) == 4
    assert orm._mock_db_results[0]['model'].id == 1
    assert orm._mock_db_results[0]['model'].col_1 == 2
    assert orm._mock_db_results[1]['model'].col_1 == 1
    assert orm._mock_db_results[1]['extra_args'] == {'fake_count': 1}
    assert orm._mock_db_results[2]['model'].id == 5
    assert orm._mock_db_results[3]['model'].col_1 == 2

    models = ModelTest.query_direct(orm, 'model')
    assert len(models) == len(data_orig)
    for i, model in enumerate(models):
        for col in ModelTest._columns:
            if col == 'col_auto_ro':
                continue
            assert data_orig[i][col] == getattr(model, col)

    rtn_cols = ['col_1', 'col_2']
    models = ModelTest.query_direct(orm, model_meta.ReturnAs.MODEL,
            rtn_cols, limit=2)
    assert len(models) == 2
    for i, model in enumerate(models):
        for col in rtn_cols:
            assert data_orig[i][col] == getattr(model, col)
        assert model.id is None

    where = ('col_1', model_meta.LogicOp.EQUALS, 2)
    order = ('id', model_meta.SortOrder.DESC)
    pd_df = ModelTest.query_direct(orm, 'pandas', where=where, order=order,
            fake_extra='fake val')
    assert len(pd_df) == 3
    data_expected = [data_orig[2], data_orig[3], data_orig[0]]
    for i in range(len(pd_df)):
        for col in ModelTest._columns:
            if col == 'col_auto_ro':
                continue
            assert pd_df.iloc[i].loc[col] == data_expected[i][col]
        assert pd_df.iloc[i].loc['extra_args'] == {'fake_extra': 'fake val'}

    caplog.clear()
    with pytest.raises(orm_meta.NonexistentColumnError) as ex:
        ModelTest.query_direct(orm, 'model', ['bad_col'])
    assert 'Invalid column(s) for ModelTest: `bad_col`' in str(ex.value)
    assert caplog.record_tuples == [
        ('tests.unit.model.test_model_meta', logging.ERROR,
            'Invalid column(s) for ModelTest: `bad_col`')
    ]



def test__get_active_data_as_dict():
    """
    Tests the `_get_active_data_as_dict()` method in `Model`.
    """
    orm = OrmTest(None)
    model = ModelTest(orm)
    assert model._get_active_data_as_dict() == {}

    model.col_1 = 'v1'
    model.col_2 = 'v2'
    model.col_auto_ro = 'ro'
    assert model._get_active_data_as_dict() == {'col_1': 'v1', 'col_2': 'v2'}
    assert model._get_active_data_as_dict(False) \
            ==  {'col_1': 'v1', 'col_2': 'v2', 'col_auto_ro': 'ro'}

    data = {
        'id': 3,
        'col_2': 'four',
    }
    model = ModelTest(orm, data)
    assert model._get_active_data_as_dict() == data
    model._active_cols.remove('id')
    assert model._get_active_data_as_dict() == {'col_2': 'four'}
    assert model._get_active_data_as_dict(False) == {'col_2': 'four'}



def test__get_where_self_id(caplog):
    """
    Tests the `_get_where_self_id()` method in `Model`.
    """
    orm = OrmTest(None)
    model = ModelTest(orm, {'id': 1})
    assert model._get_where_self_id() == ('id', model_meta.LogicOp.EQUALS, 1)

    caplog.clear()
    model.id = None
    with pytest.raises(ValueError) as ex:
        model._get_where_self_id()
    assert 'Cannot generate where clause with ID being None' in str(ex.value)
    assert caplog.record_tuples == [
        ('grand_trade_auto.model.model_meta', logging.ERROR,
            'Cannot generate where clause with ID being None')
    ]
