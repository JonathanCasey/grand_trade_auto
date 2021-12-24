#!/usr/bin/env python3
"""
Tests the grand_trade_auto.model.model_meta functionality.

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

from grand_trade_auto.model import model_meta



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
