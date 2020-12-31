#!/usr/bin/env python3
"""
Tests the grand_trade_auto.brokers.brokers functionality.

Per [pytest](https://docs.pytest.org/en/reorganize-docs/new-docs/user/naming_conventions.html),
all tiles, classes, and methods will be prefaced with `test_/Test` to comply
with auto-discovery (others may exist, but will not be part of test suite
directly).

Module Attributes:
  N/A

(C) Copyright 2020 Jonathan Casey.  All Rights Reserved Worldwide.
"""
#pylint: disable=protected-access  # Allow for purpose of testing those elements

import pytest

from grand_trade_auto.broker import brokers



def test_load_and_set_main_broker_from_config():
    """
    Tests that the `load_and_set_main_broker_from_config()` method.
    """
    with pytest.raises(AssertionError):
        brokers.load_and_set_main_broker_from_config('invalid-env')
    assert brokers._BROKER_HANDLE is None

    brokers.load_and_set_main_broker_from_config('test', 'alpaca')
    assert brokers._BROKER_HANDLE is not None
    assert brokers._BROKER_HANDLE.rest_api is not None

    with pytest.raises(AssertionError):
        brokers.load_and_set_main_broker_from_config('test')
    assert brokers._BROKER_HANDLE is not None



def test_get_broker_from_config():
    """
    Tests that the `_get_broker_from_config()` method.
    """
    assert brokers._get_broker_from_config('invalid-env') is None
    assert brokers._get_broker_from_config('test', 'invalid-type') is None
    assert brokers._get_broker_from_config('test') is not None
    assert brokers._get_broker_from_config('test', 'alpaca') is not None
