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
#pylint: disable=invalid-sequence-index              # Due to alpha_vantage code
#pylint: disable=protected-access  # Allow for purpose of testing those elements
#pylint: disable=unbalanced-tuple-unpacking          # Due to alpha_vantage code

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



def test_connect(monkeypatch, alphavantage_test):
    """
    Tests the `connect()` method in `Alphavantage`.

    Since there is nothing in that function, will test if connectivity works at
    all here.

    ** Consumes 2 API calls. **
    (failed calls do not seem to count)
    """
    # Make sure this does not cause an issue
    alphavantage_test.connect()

    time_series = TimeSeries(key=alphavantage_test._api_key)
    data, meta_data = time_series.get_intraday('MSFT', interval='1min')
    assert len(data) == 100
    assert meta_data['2. Symbol'] == 'MSFT'

    time_series = TimeSeries(key=alphavantage_test._api_key)
    with pytest.raises(ValueError) as ex:
        data, meta_data = time_series.get_intraday('INVALID', interval='1min')
    assert 'Invalid API call.' in str(ex.value)


    creds = {}
    creds['ALPHAVANTAGE_API_KEY'] = alphavantage_test._api_key
    alphavantage_test._api_key = None

    for env_var, env_creds in creds.items():
        if os.getenv(env_var) is None:
            monkeypatch.setenv(env_var, env_creds)

    time_series = TimeSeries()
    data, meta_data = time_series.get_intraday('MSFT', interval='1min')
    assert len(data) == 100
    assert meta_data['2. Symbol'] == 'MSFT'


    for env_var in creds:
        monkeypatch.delenv(env_var)

    with pytest.raises(ValueError) as ex:
        time_series = TimeSeries()
        data, meta_data = time_series.get_intraday('MSFT', interval='1min')
    assert 'The AlphaVantage API key must be provided either through the key' \
            + ' parameter or through the environment variable' \
            + ' ALPHAVANTAGE_API_KEY.' in str(ex.value)
