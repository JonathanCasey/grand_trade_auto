#!/usr/bin/env python3
"""
Tests all of the Model subclasses in the grand_trade_auto.model subpackage.

Per [pytest](https://docs.pytest.org/en/reorganize-docs/new-docs/user/naming_conventions.html),
all tiles, classes, and methods will be prefaced with `test_/Test` to comply
with auto-discovery (others may exist, but will not be part of test suite
directly).

Module Attributes:
  N/A

(C) Copyright 2021 Jonathan Casey.  All Rights Reserved Worldwide.
"""
#pylint: disable=protected-access  # Allow for purpose of testing those elements

from abc import ABC
import inspect

import pytest

from grand_trade_auto.model import company
from grand_trade_auto.model import datafeed_src
from grand_trade_auto.model import exchange
from grand_trade_auto.model import security
from grand_trade_auto.model import security_price
from grand_trade_auto.model import stock_adjustment



@pytest.mark.parametrize('model_cls, table_name, extra_attrs', [
    (datafeed_src.DatafeedSrc, 'datafeed_src', []),
    (exchange.Exchange, 'exchange', []),
    (company.Company, 'company', []),
    (security.Security, 'security', []),
    (security_price.SecurityPrice, 'security_price', []),
    (stock_adjustment.StockAdjustment, 'stock_adjustment', []),
])
def test_model_attrs(model_cls, table_name, extra_attrs):
    """
    Tests all the attributes of the provided Models to ensure it is a complete
    and expected model definition.

    The `extra_attrs` are any attributes added to a subclass of Model that are
    not in the Model abstract class nor are columns names.
    """
    assert model_cls._table_name is not None
    assert model_cls._table_name == table_name
    assert model_cls._columns is not None

    class EmptyAbstract(ABC):            #pylint: disable=too-few-public-methods
        """
        Empty abstract class to facilitate getting list of standard attrs.
        """

    class EmptyClass(EmptyAbstract):     #pylint: disable=too-few-public-methods
        """
        Empty class to facilitate getting list of standard attrs.
        """

    model_attrs = {m[0] for m in inspect.getmembers(model_cls)
            if not inspect.isroutine(m[1])}
    std_attrs = {m[0] for m in inspect.getmembers(EmptyClass)
            if not inspect.isroutine(m[1])}
    col_attrs = set(model_cls._columns)
    other_req_attrs = {
        '_table_name',
        '_columns',
    }
    extra_attrs = set(extra_attrs)

    assert col_attrs.issubset(model_attrs)
    assert extra_attrs.issubset(model_attrs)
    assert std_attrs.issubset(model_attrs)
    assert not model_attrs \
            - std_attrs - col_attrs - other_req_attrs - extra_attrs
