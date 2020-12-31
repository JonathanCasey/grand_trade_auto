#!/usr/bin/env python3
"""
Tests the grand_trade_auto.general.broker_alpaca functionality.

Per [pytest](https://docs.pytest.org/en/reorganize-docs/new-docs/user/naming_conventions.html),
all tiles, classes, and methods will be prefaced with `test_/Test` to comply
with auto-discovery (others may exist, but will not be part of test suite
directly).

Module Attributes:
  N/A

(C) Copyright 2020 Jonathan Casey.  All Rights Reserved Worldwide.
"""
#pylint: disable=protected-access  # Allow for purpose of testing those elements

import configparser
import logging
import os
from types import SimpleNamespace

import alpaca_trade_api
import pytest

from grand_trade_auto.broker import broker_alpaca
from grand_trade_auto.broker import brokers
from grand_trade_auto.general import config



@pytest.fixture(name='alpaca_test_handle')
def fixture_alpaca_test_handle():
    """
    Gets the test broker handle for alpaca.

    Returns:
      (BrokerAlpaca): The test alpaca broker handle.
    """
    return brokers._get_broker_from_config('test', 'alpaca')



def test_load_from_config(alpaca_test_handle):
    """
    Tests the `load_from_config()` method in `BrokerAlpaca`.

    TODO: This should load its own conf files and test directly; but good enough
    for now.
    """
    assert alpaca_test_handle is not None



def test_get_type_names():
    """
    Tests the `get_type_names()` method in `BrokerAlpaca`.  Not an
    exhaustive test.
    """
    assert 'alpaca' in broker_alpaca.BrokerAlpaca.get_type_names()
    assert 'not-alpaca' not in broker_alpaca.BrokerAlpaca.get_type_names()



def test_connect(caplog, monkeypatch, alpaca_test_handle):
    """
    Tests the `connect()` method in `BrokerAlpaca`.
    """
    caplog.set_level(logging.INFO)
    caplog.clear()
    alpaca_test_handle.connect('rest')
    assert alpaca_test_handle.rest_api is not None
    assert caplog.record_tuples == [
            ('grand_trade_auto.broker.broker_alpaca', logging.INFO,
                'Established connection to Alpaca via REST.')
    ]

    caplog.clear()
    alpaca_test_handle.connect('rest')
    assert alpaca_test_handle.rest_api is not None
    assert caplog.record_tuples == []

    with pytest.raises(NotImplementedError) as ex:
        alpaca_test_handle.connect('stream')
    assert 'Stream connection not implemented for Alpaca' in str(ex.value)

    alpaca_test_handle.stream_conn = 'dummy conn'
    alpaca_test_handle.connect('stream')
    assert alpaca_test_handle.stream_conn == 'dummy conn'

    with pytest.raises(ValueError) as ex:
        alpaca_test_handle.connect('invalid interface')
    assert 'Invalid interface for Alpaca' in str(ex.value)


    def mock_read_conf_file(file):             # pylint: disable=unused-argument
        """
        Replaces the conf file reader with a dummy ConfigParser.
        """
        mock_cp = configparser.ConfigParser()
        mock_cp[alpaca_test_handle.cp_broker_id] = {
                'api key id': 'dummy key id',
        }
        mock_cp[alpaca_test_handle.cp_secrets_id] = {
                'secret key': 'dummy secret key',
        }
        return mock_cp

    monkeypatch.setattr(config, 'read_conf_file', mock_read_conf_file)

    caplog.clear()
    alpaca_test_handle.rest_api = None
    with pytest.raises(ConnectionRefusedError) as ex:
        alpaca_test_handle.connect('rest')
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

    # Ok to leave old monkeypatch for read_conf_file
    monkeypatch.setattr(alpaca_trade_api, 'REST', mock_get_rest_api)

    caplog.clear()
    alpaca_test_handle.rest_api = None
    with pytest.raises(ConnectionRefusedError) as ex:
        alpaca_test_handle.connect('rest')
    assert 'Unable to connect to Alpaca.  Account status:' in str(ex.value)
    assert 'not active' in str(ex.value)



def test_connect_env(caplog, monkeypatch, alpaca_test_handle):
    """
    Tests the `connect()` method in `BrokerAlpaca`; specifically, the fallback
    of usinv environment variables for credentials.

    Want to read with env variables first if possible, then without any env
    variables at all.
    """
    caplog.set_level(logging.INFO)

    broker_cp = config.read_conf_file('brokers.conf')
    secrets_cp = config.read_conf_file('.secrets.conf')

    creds = {}
    creds['APCA_API_KEY_ID'] = broker_cp.get(alpaca_test_handle.cp_broker_id,
            'api key id', fallback=None)
    creds['APCA_API_KEY_ID'] = secrets_cp.get(alpaca_test_handle.cp_secrets_id,
            'api key id', fallback=creds['APCA_API_KEY_ID'])
    creds['APCA_API_SECRET_KEY'] = secrets_cp.get(
            alpaca_test_handle.cp_secrets_id, 'secret key', fallback=None)


    def mock_read_conf_file_empty(file):       # pylint: disable=unused-argument
        """
        Replaces the conf file reader with an empty ConfigParser.
        """
        return configparser.ConfigParser()

    monkeypatch.setattr(config, 'read_conf_file', mock_read_conf_file_empty)

    caplog.clear()
    alpaca_test_handle.rest_api = None
    for env_var in creds:
        if os.getenv(env_var) is None:
            monkeypatch.setenv(env_var, creds[env_var])

    alpaca_test_handle.connect('rest')
    assert alpaca_test_handle.rest_api is not None
    assert caplog.record_tuples == [
            ('grand_trade_auto.broker.broker_alpaca', logging.INFO,
                'Established connection to Alpaca via REST.')
    ]


    caplog.clear()
    alpaca_test_handle.rest_api = None
    for env_var in creds:
        monkeypatch.delenv(env_var)

    with pytest.raises(ConnectionRefusedError) as ex:
        alpaca_test_handle.connect('rest')
    assert 'Unable to connect to Alpaca.  API Error:' in str(ex.value)
    assert 'Key ID must be given' in str(ex.value)
