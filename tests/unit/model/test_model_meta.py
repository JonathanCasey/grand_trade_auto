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

import logging

import pytest

from grand_trade_auto.model import model_meta
from grand_trade_auto.model import orm_meta



logger = logging.getLogger(__name__)



def test_enum_return_as():
    """
    Tests the essential items of the `ReturnAs` Enum in `model_meta`.
    """
    # Must test enum values since this allows access by value
    assert model_meta.ReturnAs('model') == model_meta.ReturnAs.MODEL
    assert model_meta.ReturnAs('pandas') == model_meta.ReturnAs.PANDAS
    assert len(model_meta.ReturnAs) == 2



def test_enum_logic_op():
    """
    Tests the essential items of the `LogicOp` Enum in `model_meta`.
    """
    # Do not need to test values since access by value unsupported
    names = {'EQUAL', 'EQUALS', 'EQ', 'LESS_THAN', 'LT',
            'LESS_THAN_OR_EQUAL', 'LTE', 'GREATER_THAN', 'GT',
            'GREATER_THAN_OR_EQUAL', 'GTE', 'NOT_NULL'}
    assert names == {e.name for e in list(model_meta.LogicOp)}



def test_enum_logic_combo():
    """
    Tests the essential items of the `LogicCombo` Enum in `model_meta`.
    """
    # Do not need to test values since access by value unsupported
    names = {'AND', 'OR'}
    assert names == {e.name for e in list(model_meta.LogicCombo)}



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
    )

    # Column Attributes -- MUST match _columns!
    # id defined in super
    col_1 = None
    col_2 = None
    # End of Column Attributes



class OrmTest(orm_meta.Orm):
    """
    A barebones Orm that can be used for most tests.

    Class/Instance Attributes:
      mock_db_results ([]): A list of objects that would be in the database if
        there were a db.  Meant to store results for add() so they can be
        checked later, etc.
    """
    _mock_db_results = []

    def _create_schema_datafeed_src(self):
        """
        Not needed / will not be used.
        """

    def add(self, model_cls, data, **kwargs):
        """
        Fake adding something to mock results, and check cols.  Expected to
        check afterwards.
        """
        OrmTest._validate_cols(data.keys(), model_cls)
        res = {
            'model': model_cls(self, data),
            'extra_args': kwargs,
        }
        self._mock_db_results.append(res)


    def update(self, model_cls, data, where, **kwargs):
        """
        Fake updating something in mock results, and check cols.  Expected to
        have existing data.  Limited 'where' clause support.
        """


    def delete(self, model_cls, where, really_delete_all=False, **kwargs):
        """
        Fake deleting something in mock results, and check cols.  Expected to
        have existing data.  Limited 'where' clause support.
        """


    def query(self, model_cls, return_as, columns_to_return=None,
            where=None, limit=None, order=None, **kwargs):
        """
        Fake querying something from mock results, and check cols.  Expected to
        have existing data.  Limited 'where' and 'order' clause support.
        """


    @staticmethod
    def _validate_cols(cols, model_cls):
        """
        A helper method just for this testing to check columns, raise an
        exception if there is an issue.
        """
        valid_cols = model_cls.get_columns()
        if not set(cols).issubset(valid_cols):
            err_msg = f'Invalid column(s) for {model_cls.__name__}:'
            err_msg += f' `{"`, `".join(set(cols) - set(valid_cols))}`'
            logger.error(err_msg)
            raise orm_meta.NonexistentColumnError(err_msg)



def test_model_init():
    """
    Tests the `__init__()` method in `Model`.
    """
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
    data = {'id': 3, 'bad_col': 4}
    with pytest.raises(AssertionError) as ex:
        ModelTest('', data)
    assert 'Invalid data column: bad_col' in str(ex.value)



def test_model_setattr():
    """
    Tests the `__setattr__()` method in `Model`.
    """
    model = ModelTest('')
    assert model._active_cols == set()

    model.id = 1
    assert model._active_cols == set(['id'])
    assert model.id == 1

    model._table_name = 'not active col'
    assert model._active_cols == set(['id'])
    assert model._table_name == 'not active col'



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
    assert ModelTest.get_columns() == ('id', 'col_1', 'col_2')
    assert model.get_columns() == ('id', 'col_1', 'col_2')



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
    assert len(orm._mock_db_results) == 1
    res = orm._mock_db_results[1]
    assert res['model'].id is None
    assert res['model'].col_1 is None   # Removed from active, should be skipped
    assert res['model'].col_2 == 4
    assert res['extra_args'] == {'cursor': 'fake_cursor', 'conn': 4}

    caplog.clear()
    with pytest.raises(orm_meta.NonexistentColumnError) as ex:
        ModelTest.add_direct(orm, {'bad_col': 5})
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
        cols['bad_col'] = 6
        return cols

    caplog.clear()
    monkeypatch.setattr(ModelTest, '_get_active_data_as_dict',
            mock_get_active_data_as_dict)
    data_3 = {
        'col_1': 7,
    }
    model = ModelTest(orm, data_3)
    with pytest.raises(orm_meta.NonexistentColumnError) as ex:
        model.add()
    assert 'Invalid column(s) for ModelTest: `bad_col`' in str(ex.value)
    assert caplog.record_tuples == [
        ('tests.unit.model.test_model_meta', logging.ERROR,
            'Invalid column(s) for ModelTest: `bad_col`')
    ]
