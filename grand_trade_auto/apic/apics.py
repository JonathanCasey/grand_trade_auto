#!/usr/bin/env python3
"""
The API Client access module.  This is intended to be the item accessed outside
of the API Client submodule/folder.

Module Attributes:
  _APIC (Apic<>): The handle to the API Client that will be used, where Apic<>
    is a subclass of Apic (e.g. Alpaca).

(C) Copyright 2021 Jonathan Casey.  All Rights Reserved Worldwide.
"""
from grand_trade_auto.apic import alpaca
from grand_trade_auto.general import config



_APIC = None    # Init'd later; but once init'd, should never change



def load_and_set_main_apic_from_config(env, provider=None):
    """
    Loads the main API Client from config and sets it as the main handle open.

    Arg:
      env (str): The environment for which to load the API Client config.
      provider (str or None): The API Client provider type to be forced as the
        one to load; or None to simply take the first one found.

    Raises:
      (AssertionError): Raised if API Client already loaded or cannot be loaded.
    """
    global _APIC                              # pylint: disable=global-statement
    assert _APIC is None, 'Cannot load API Clients: API Client already loaded.'
    apic = _get_apic_from_config(env, provider)
    if apic is not None:
        _APIC = apic
        # TEMP: connecting here for testing purposes
        apic.connect()
    assert _APIC is not None, 'No valid API Client configuration found.'



def _get_apic_from_config(env, provider=None):
    """
    Loads the API Clients from the config file and sets the first one it finds
    to be the valid one to use.  Stores for later access.

    Arg:
      env (str): The environment for which to load the API Client config.
      provider (str or None): The API Client provider type to be forced as the
        one to load; or None to simply take the first one found.

    Raises:
      (AssertionError): Raised if API Client already loaded or cannot be loaded.
    """
    apic_cp = config.read_conf_file('apics.conf')
    secrets_cp = config.read_conf_file('.secrets.conf')

    for apic_id in apic_cp.sections():
        if env != apic_cp[apic_id]['env'].strip():
            continue

        secrets_id = config.get_matching_secrets_id(secrets_cp, 'apic', apic_id)

        alpaca_provider_names = alpaca.Alpaca.get_provider_names()
        if apic_cp[apic_id]['provider'].strip() in alpaca_provider_names:
            if provider is not None and provider not in alpaca_provider_names:
                continue

            apic = alpaca.Alpaca.load_from_config(apic_cp, apic_id, secrets_id)

            if apic is not None:
                return apic
    return None
