#!/usr/bin/env python3
"""
Tests the grand_trade_auto.apic.alphavantage functionality.

Per [pytest](https://docs.pytest.org/en/reorganize-docs/new-docs/user/naming_conventions.html),
all tiles, classes, and methods will be prefaced with `test_/Test` to comply
with auto-discovery (others may exist, but will not be part of test suite
directly).

Module Attributes:
  N/A

(C) Copyright 2021 Jonathan Casey.  All Rights Reserved Worldwide.
"""
#pylint: disable=protected-access  # Allow for purpose of testing those elements

import logging
import os

from alpha_vantage.timeseries import TimeSeries
import pytest

from grand_trade_auto.apic import alphavantage
from grand_trade_auto.apic import apics



@pytest.fixture(name='alphavantage_test')
def fixture_alphavantage_test():
    """
    Gets the test API Client handle for Alpha Vantage.

    Returns:
      (Alphavantage): The test Alpha Vantage API Client handle.
    """
    # This also ensures its support was added to apics.py
    return apics._get_apic_from_config('alphavantage-test', 'test')



def test_load_from_config(alphavantage_test):
    """
    Tests the `load_from_config()` method in `Alphavantage`.

    TODO: This should load its own conf files and test directly; but good enough
    for now.
    """
    assert alphavantage_test is not None



def test_get_provider_names():
    """
    Tests the `get_provider_names()` method in `Alpaca`.  Not an exhaustive
    test.
    """
    assert 'alphavantage' in alphavantage.Alphavantage.get_provider_names()
    assert 'not-alphavantage' \
            not in alphavantage.Alphavantage.get_provider_names()
