#!/usr/bin/env python3
"""
The broker API module.  This is intended to be the item accessed outside of
the broker submodule/folder.

Module Attributes:
  _BROKER_HANDLE (BrokerMeta<>): The handle to the broker that will be used,
    where BrokerMeta<> is a subclass of BrokerMeta (e.g. BrokerAlpaca).

(C) Copyright 2020 Jonathan Casey.  All Rights Reserved Worldwide.
"""
from grand_trade_auto.broker import broker_alpaca
from grand_trade_auto.general import config



_BROKER_HANDLE = None   # Init'd later; but once init'd, should never change



def load_and_set_main_broker_from_config(env, broker_type=None):
    """
    Loads the main broker from config and sets it as the main handle open.

    Arg:
      env (str): The environment for which to load broker config.
      broker_type (str or None): The broker type to be forced as the one to
        load; or None to simply take the first one found.

    Raises:
      (AssertionError): Raised if broker already loaded or cannot be loaded.
    """
    global _BROKER_HANDLE    # pylint: disable=global-statement
    assert _BROKER_HANDLE is None, 'Cannot load brokers: Broker already loaded.'
    broker_handle = _get_broker_from_config(env, broker_type)
    if broker_handle is not None:
        _BROKER_HANDLE = broker_handle
        # TEMP: connecting here for testing purposes
        broker_handle.connect()
    assert _BROKER_HANDLE is not None, 'No valid broker configuration found.'



def _get_broker_from_config(env, broker_type=None):
    """
    Loads the brokers from the config file and sets the first one it finds to
    be the valid one to use.  Stores for later access.

    Arg:
      env (str): The environment for which to load broker config.
      broker_type (str or None): The broker type to be forced as the one to
        load; or None to simply take the first one found.

    Raises:
      (AssertionError): Raised if broker already loaded or cannot be loaded.
    """
    broker_cp = config.read_conf_file('brokers.conf')
    secrets_cp = config.read_conf_file('.secrets.conf')

    for broker_id in broker_cp.sections():
        if env != broker_cp[broker_id]['env'].strip():
            continue

        secrets_id = config.get_matching_secrets_id(secrets_cp, 'broker',
                broker_id)

        alpaca_type_names = broker_alpaca.BrokerAlpaca.get_type_names()
        if broker_cp[broker_id]['type'].strip() in alpaca_type_names:
            if broker_type is not None and broker_type not in alpaca_type_names:
                continue

            broker_handle = broker_alpaca.BrokerAlpaca.load_from_config(
                    broker_cp, broker_id, secrets_cp, secrets_id)

            if broker_handle is not None:
                return broker_handle
    return None
