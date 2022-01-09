#!/usr/bin/env python3
"""
Tests the grand_trade_auto.model.model_meta functionality.

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

import pandas as pd
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
    #pylint: disable=multi-line-list-first-line-item, multi-line-list-eol-close
    #pylint: disable=closing-comma
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



class OrmTest(orm_meta.Orm):
    """
    A barebones Orm that can be used for most tests.
    """
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
        Logs inputs so call from Model can be verified.
        """
        logger.info(f'adding model_cls: {model_cls}' )
        logger.info(f'data: { {k: data[k] for k in sorted(data)} }')
        logger.info(f'kwargs: {kwargs}')



    def update(self, model_cls, data, where, **kwargs):
        """
        Logs inputs so call from Model can be verified.
        """
        logger.info(f'updating model_cls: {model_cls}' )
        logger.info(f'data: { {k: data[k] for k in sorted(data)} }')
        logger.info(f'where: {where}')
        logger.info(f'kwargs: {kwargs}')



    def delete(self, model_cls, where, really_delete_all=False, **kwargs):
        """
        Logs inputs so call from Model can be verified.
        """
        logger.info(f'deleting model_cls: {model_cls}' )
        logger.info(f'really_delete_all: {really_delete_all}')
        logger.info(f'where: {where}')
        logger.info(f'kwargs: {kwargs}')



    def query(self, model_cls, return_as, columns_to_return=None,
            where=None, limit=None, order=None, **kwargs):
        """
        Logs inputs so call from Model can be verified.  Returns empty dummy
        values.
        """
        logger.info(f'querying model_cls: {model_cls}' )
        logger.info(f'return_as: {return_as}')
        logger.info(f'columns_to_return: {columns_to_return}')
        logger.info(f'where: {where}')
        logger.info(f'limit: {limit}')
        logger.info(f'order: {order}')
        logger.info(f'kwargs: {kwargs}')

        if model_meta.ReturnAs(return_as) is model_meta.ReturnAs.MODEL:
            return [ModelTest(OrmTest(None))]
        if model_meta.ReturnAs(return_as) is model_meta.ReturnAs.PANDAS:
            return pd.DataFrame()
        raise ValueError('Test Error: Provided ReturnAs not supported')



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



def test_add_and_direct(caplog):
    """
    Tests the `add()` and `add_direct()` methods in `Model`.
    """
    caplog.set_level(logging.INFO)

    orm = OrmTest(None)

    caplog.clear()
    data_1 = {
        'col_1': 1,
        'col_2': 2,
    }
    ModelTest.add_direct(orm, data_1, conn='fake_conn')
    assert caplog.record_tuples == [
        ('tests.unit.model.test_model_meta', logging.INFO,
            "adding model_cls:"
                + " <class 'tests.unit.model.test_model_meta.ModelTest'>"),
        ('tests.unit.model.test_model_meta', logging.INFO,
            "data: {'col_1': 1, 'col_2': 2}"),
        ('tests.unit.model.test_model_meta', logging.INFO,
            "kwargs: {'conn': 'fake_conn'}"),
    ]

    caplog.clear()
    data_2 = {
        'col_1': 3,
        'col_2': 4,
    }
    model = ModelTest(orm, data_2)
    model._active_cols.remove('col_1')
    model.add(cursor='fake_cursor', conn=4)
    assert caplog.record_tuples == [
        ('tests.unit.model.test_model_meta', logging.INFO,
            "adding model_cls:"
                + " <class 'tests.unit.model.test_model_meta.ModelTest'>"),
        ('tests.unit.model.test_model_meta', logging.INFO,
            "data: {'col_2': 4}"),
        ('tests.unit.model.test_model_meta', logging.INFO,
            "kwargs: {'cursor': 'fake_cursor', 'conn': 4}"),
    ]



def test_update_and_direct(caplog):
    """
    Tests the `update()` and `udpate_direct()` methods in `Model`.
    """
    caplog.set_level(logging.INFO)

    orm = OrmTest(None)

    caplog.clear()
    new_data_1 = {
        'id': 4,
        'col_1': 5,
    }
    where_1 = ('col_1', model_meta.LogicOp.EQUALS, 1)
    ModelTest.update_direct(orm, new_data_1, where_1, new_fake=True)
    assert caplog.record_tuples == [
        ('tests.unit.model.test_model_meta', logging.INFO,
            "updating model_cls:"
                + " <class 'tests.unit.model.test_model_meta.ModelTest'>"),
        ('tests.unit.model.test_model_meta', logging.INFO,
            "data: {'col_1': 5, 'id': 4}"),
        ('tests.unit.model.test_model_meta', logging.INFO,
            "where: ('col_1', <LogicOp.EQUALS: '='>, 1)"),
        ('tests.unit.model.test_model_meta', logging.INFO,
            "kwargs: {'new_fake': True}"),
    ]

    caplog.clear()
    new_data_2 = {
        'id': 2,
        'col_1': 6,
    }
    model = ModelTest(orm, new_data_2)
    model.col_auto_ro = 'allowed but ignored'
    model.update(another_fake=9)
    assert caplog.record_tuples == [
        ('tests.unit.model.test_model_meta', logging.INFO,
            "updating model_cls:"
                + " <class 'tests.unit.model.test_model_meta.ModelTest'>"),
        ('tests.unit.model.test_model_meta', logging.INFO,
            "data: {'col_1': 6, 'id': 2}"),
        ('tests.unit.model.test_model_meta', logging.INFO,
            "where: ('id', <LogicOp.EQUALS: '='>, 2)"),
        ('tests.unit.model.test_model_meta', logging.INFO,
            "kwargs: {'another_fake': 9}"),
    ]



def test_delete_and_direct(caplog):
    """
    Tests the `update()` and `udpate_direct()` methods in `Model`.
    """
    caplog.set_level(logging.INFO)

    orm = OrmTest(None)

    caplog.clear()
    where_1 = ('col_1', model_meta.LogicOp.EQUALS, 2)
    ModelTest.delete_direct(orm, where_1, fake_arg=1)
    assert caplog.record_tuples == [
        ('tests.unit.model.test_model_meta', logging.INFO,
            "deleting model_cls:"
                + " <class 'tests.unit.model.test_model_meta.ModelTest'>"),
        ('tests.unit.model.test_model_meta', logging.INFO,
            'really_delete_all: False'),
        ('tests.unit.model.test_model_meta', logging.INFO,
            "where: ('col_1', <LogicOp.EQUALS: '='>, 2)"),
        ('tests.unit.model.test_model_meta', logging.INFO,
            "kwargs: {'fake_arg': 1}"),
    ]

    caplog.clear()
    ModelTest.delete_direct(orm, where_1, really_delete_all=True, fake_arg=1)
    assert caplog.record_tuples == [
        ('tests.unit.model.test_model_meta', logging.INFO,
            "deleting model_cls:"
                + " <class 'tests.unit.model.test_model_meta.ModelTest'>"),
        ('tests.unit.model.test_model_meta', logging.INFO,
            'really_delete_all: True'),
        ('tests.unit.model.test_model_meta', logging.INFO,
            "where: ('col_1', <LogicOp.EQUALS: '='>, 2)"),
        ('tests.unit.model.test_model_meta', logging.INFO,
            "kwargs: {'fake_arg': 1}"),
    ]

    caplog.clear()
    data_1 = {
        'id': 1,
    }
    model = ModelTest(orm, data_1)
    model.delete(another_fake=True)
    assert caplog.record_tuples == [
        ('tests.unit.model.test_model_meta', logging.INFO,
            "deleting model_cls:"
                + " <class 'tests.unit.model.test_model_meta.ModelTest'>"),
        ('tests.unit.model.test_model_meta', logging.INFO,
            'really_delete_all: False'),
        ('tests.unit.model.test_model_meta', logging.INFO,
            "where: ('id', <LogicOp.EQUALS: '='>, 1)"),
        ('tests.unit.model.test_model_meta', logging.INFO,
            "kwargs: {'another_fake': True}"),
    ]



def test_query_direct(caplog):
    """
    Tests the `query_direct()` method in `Model`.
    """
    caplog.set_level(logging.INFO)

    orm = OrmTest(None)

    caplog.clear()
    models = ModelTest.query_direct(orm)
    assert len(models) == 1
    assert isinstance(models[0], ModelTest)
    assert caplog.record_tuples == [
        ('tests.unit.model.test_model_meta', logging.INFO,
            "querying model_cls:"
                + " <class 'tests.unit.model.test_model_meta.ModelTest'>"),
        ('tests.unit.model.test_model_meta', logging.INFO,
            'return_as: ReturnAs.MODEL'),
        ('tests.unit.model.test_model_meta', logging.INFO,
            'columns_to_return: None'),
        ('tests.unit.model.test_model_meta', logging.INFO,
            'where: None'),
        ('tests.unit.model.test_model_meta', logging.INFO,
            'limit: None'),
        ('tests.unit.model.test_model_meta', logging.INFO,
            "order: None"),
        ('tests.unit.model.test_model_meta', logging.INFO,
            "kwargs: {}"),
    ]

    caplog.clear()
    where = ('col_1', model_meta.LogicOp.EQUALS, 2)
    order = ('id', model_meta.SortOrder.DESC)
    pd_df = ModelTest.query_direct(orm, 'pandas', ['col_2'], where, 3, order,
            fake_extra='fake val')
    assert isinstance(pd_df, pd.DataFrame)
    assert caplog.record_tuples == [
        ('tests.unit.model.test_model_meta', logging.INFO,
            "querying model_cls:"
                + " <class 'tests.unit.model.test_model_meta.ModelTest'>"),
        ('tests.unit.model.test_model_meta', logging.INFO,
            'return_as: pandas'),
        ('tests.unit.model.test_model_meta', logging.INFO,
            "columns_to_return: ['col_2']"),
        ('tests.unit.model.test_model_meta', logging.INFO,
            "where: ('col_1', <LogicOp.EQUALS: '='>, 2)"),
        ('tests.unit.model.test_model_meta', logging.INFO,
            'limit: 3'),
        ('tests.unit.model.test_model_meta', logging.INFO,
            "order: ('id', <SortOrder.DESC: 'desc'>)"),
        ('tests.unit.model.test_model_meta', logging.INFO,
            "kwargs: {'fake_extra': 'fake val'}"),
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
            'Cannot generate where clause with ID being None'),
    ]
