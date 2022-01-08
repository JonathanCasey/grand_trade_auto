#!/usr/bin/env python3
"""
Tests the grand_trade_auto.apic.alpaca functionality.

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
from types import SimpleNamespace

import alpaca_trade_api
import pytest

from grand_trade_auto.apic import alpaca
from grand_trade_auto.apic import apics



@pytest.fixture(name='alpaca_test')
def fixture_alpaca_test():
    """
    Gets the test API Client handle for alpaca.

    Returns:
      (Alpaca): The test alpaca API Client handle.
    """
    # This also ensures its support was added to apics.py
    return apics._get_apic_from_config('alpaca-test', 'test')



def test_load_from_config(alpaca_test):
    """
    Tests the `load_from_config()` method in `Alpaca`.

    TODO: This should load its own conf files and test directly; but good enough
    for now.
    """
    assert alpaca_test is not None



def test_get_provider_names():
    """
    Tests the `get_provider_names()` method in `Alpaca`.  Not an exhaustive
    test.
    """
    assert 'alpaca' in alpaca.Alpaca.get_provider_names()
    assert 'not-alpaca' not in alpaca.Alpaca.get_provider_names()



def test_connect(caplog, monkeypatch, alpaca_test):
    """
    Tests the `connect()`/`_connect()` method in `Alpaca`.
    """
    caplog.set_level(logging.INFO)
    caplog.clear()
    alpaca_test.connect()
    assert alpaca_test._rest_api is not None
    assert caplog.record_tuples == [
            ('grand_trade_auto.apic.alpaca', logging.INFO,
                'Established connection to Alpaca via REST.'),
    ]

    caplog.clear()
    alpaca_test._connect('rest')
    assert alpaca_test._rest_api is not None
    assert caplog.record_tuples == []

    with pytest.raises(NotImplementedError) as ex:
        alpaca_test._connect('stream')
    assert 'Stream connection not implemented for Alpaca' in str(ex.value)

    alpaca_test._stream_conn = 'dummy conn'
    alpaca_test._connect('stream')
    assert alpaca_test._stream_conn == 'dummy conn'

    with pytest.raises(ValueError) as ex:
        alpaca_test._connect('invalid interface')
    assert 'Invalid interface for Alpaca' in str(ex.value)

    caplog.clear()
    alpaca_test._rest_api = None
    alpaca_test._key_id = 'dummy key id'
    alpaca_test._secret_key = 'dummy secret key'
    with pytest.raises(ConnectionRefusedError) as ex:
        alpaca_test._connect('rest')
    assert 'Unable to connect to Alpaca.  API Error:' in str(ex.value)
    assert '(Code = 40110000)' in str(ex.value)


    class MockRestApiAccount:           # pylint: disable=too-few-public-methods
        """
        Simple mock object to be used for testing.
        """
        @staticmethod
        def get_account():
            """
            Create a dummy account response so status will not be active.
            """
            mock_account = SimpleNamespace()
            mock_account.status = 'not active'
            return mock_account

    def mock_get_rest_api(**kwargs):           # pylint: disable=unused-argument
        """
        Replaces the call to get the rest API.
        """
        return MockRestApiAccount()

    # Ok to leave invalid dummy creds from earlier test
    monkeypatch.setattr(alpaca_trade_api, 'REST', mock_get_rest_api)

    caplog.clear()
    alpaca_test._rest_api = None
    with pytest.raises(ConnectionRefusedError) as ex:
        alpaca_test._connect('rest')
    assert 'Unable to connect to Alpaca.  Account status:' in str(ex.value)
    assert 'not active' in str(ex.value)



def test_connect_env(caplog, monkeypatch, alpaca_test):
    """
    Tests the `connect()` method in `Alpaca`; specifically, the fallback of
    using environment variables for credentials.

    Want to read with env variables first if possible, then without any env
    variables at all.
    """
    caplog.set_level(logging.INFO)

    creds = {}
    creds['APCA_API_KEY_ID'] = alpaca_test._key_id
    creds['APCA_API_SECRET_KEY'] = alpaca_test._secret_key
    alpaca_test._key_id = None
    alpaca_test._secret_key = None


    caplog.clear()
    alpaca_test._rest_api = None
    for env_var, env_creds in creds.items():
        if os.getenv(env_var) is None:
            monkeypatch.setenv(env_var, env_creds)

    alpaca_test._connect('rest')
    assert alpaca_test._rest_api is not None
    assert caplog.record_tuples == [
            ('grand_trade_auto.apic.alpaca', logging.INFO,
                'Established connection to Alpaca via REST.'),
    ]


    caplog.clear()
    alpaca_test._rest_api = None
    for env_var in creds:
        monkeypatch.delenv(env_var)

    with pytest.raises(ConnectionRefusedError) as ex:
        alpaca_test._connect('rest')
    assert 'Unable to connect to Alpaca.  API Error:' in str(ex.value)
    assert 'Key ID must be given' in str(ex.value)
